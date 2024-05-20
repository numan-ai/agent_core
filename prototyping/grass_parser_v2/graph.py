import bisect

from collections import defaultdict
from dataclasses import dataclass
import random
from typing import Hashable, Optional
from uuid import uuid4

from prototyping.grass_parser_v2.server import send_updates, positions_cache


@dataclass(slots=True)
class Edge:
    start: str
    end: str
    type_name: str
    index: int = -1

    def __lt__(self, other):
        return (
            self.start, self.end, self.type_name, self.index
        ) < (
            other.start, other.end, other.type_name, other.index
        )
    
    def reverse(self):
        return type(self)(
            start=self.end,
            end=self.start,
            type_name=self.type_name,
            index=self.index
        )


class NodeEnergyMap:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.energies = defaultdict(float)
        self.energy_queue = []
        self.__energies_uncommitted = defaultdict(float)
        self.__propagated_energy = defaultdict(float)
        self.__reverse_propagated_energy = defaultdict(float)
        self._energy_decay_factor = 1.0
        self.max_iterations = 1000

    def add_energy(self, node: Hashable, energy: float, propagation: dict[float], commit: bool = False):
        """ Linearly add energy to a node and propagate it to connected nodes. """
        self._add_energy(node, energy / self._energy_decay_factor, propagation)
        
        if commit:
            for node, energy in self.__propagated_energy.items():
                self.energies[node] += energy
        else:
            for node, energy in self.__propagated_energy.items():
                self.__energies_uncommitted[node] += energy
        
        self.__propagated_energy.clear()
        
    def _send_ws_data(self):
        concept_to_id_map = {
            concept: f"_{concept}"
            for concept in self.graph.nodes_set
        }

        for node in self.graph.nodes_set:
            node_id = concept_to_id_map[node]
            if node_id not in positions_cache:
                positions_cache[node_id] = {
                    "x": random.randint(0, 1000),
                    "y": random.randint(0, 1000),
                }

        edges = [
            {
                "source": concept_to_id_map[edge.start],
                "target": concept_to_id_map[edge.end],
                "label": str(edge.index) if edge.index != -1 else "",
                "type": edge.type_name,
                "weight": 10,
            }
            for pq in list(self.graph.priority_queues.values())
            for energy, edge in pq
            if edge.start != '' and edge.end != ''
        ]
        nodes = [{
            "id": concept_to_id_map[concept],
            "label": concept,
            "weight": self.__propagated_energy.get(concept, 0) * 150,
            "x": positions_cache.get(concept_to_id_map[concept], {}).get("x", random.randint(0, 1000)),
            "y": positions_cache.get(concept_to_id_map[concept], {}).get("y", random.randint(0, 1000)),
        } for concept in self.graph.nodes_set if concept != '']
        send_updates({
            "nodes": nodes,
            "edges": edges,
        })

    def _add_energy(self, node: Hashable, energy: float, propagation: dict[float]):
        self.__propagated_energy[node] += energy

        self._send_ws_data()

        if energy < 0.05:
            return
        
        breakpoint()
        
        # propagate energy to connected nodes
        iteration_limit = min(self.max_iterations, len(self.graph.priority_queues[node]))
        for i in range(iteration_limit):
            association_weight, edge = self.graph.priority_queues[node][i]
            associated_node = edge.end
            already_propagated_energy = self.__propagated_energy[associated_node]
            _propagation = propagation[edge.type_name]
            energy_to_propagate = -association_weight * energy * _propagation
            energy_to_propagate = energy_to_propagate - already_propagated_energy
            if energy_to_propagate <= 0.0:
                continue
            self._add_energy(associated_node, energy_to_propagate, propagation)

    def reverse_propagate(self, propagation: float = 1.0):
        for node, energy in self.__energies_uncommitted.items():
            self.__reverse_propagated_energy[node] -= energy
        
        for node, energy in self.__energies_uncommitted.items():
            self._reverse_propagate(node, energy, propagation)

        self.__energies_uncommitted.clear()
        self.__reverse_propagated_energy.clear()

    def _reverse_propagate(self, node: Hashable, energy: float, propagation: float = 1.0):
        self.energies[node] += energy
        self.__reverse_propagated_energy[node] += energy
        if energy < 0.05:
            return
        
        # reverse propagate energy to connected nodes
        iteration_limit = min(self.max_iterations, len(self.graph.reverse_priority_queues[node]))
        for i in range(iteration_limit):
            association_weight, edge = self.graph.reverse_priority_queues[node][i]
            associated_node = edge.end
            already_propagated_energy = max(self.__reverse_propagated_energy[associated_node], 0)
            energy_to_propagate = -association_weight * energy * propagation
            energy_to_propagate = energy_to_propagate - already_propagated_energy
            if energy_to_propagate <= 0.0:
                continue
            self._reverse_propagate(associated_node, energy_to_propagate, propagation)

    def get_energy(self, node: Hashable):
        return self.energies[node]
    
    def get_uncommitted_energies(self):
        return self.__energies_uncommitted


class Graph:
    def __init__(self, edges: list[Edge]) -> None:
        self.priority_queues: dict[list[tuple[float, Edge]]] = defaultdict(list)
        self.reverse_priority_queues: dict[list[tuple[float, Edge]]] = defaultdict(list)
        self.incoming_nodes = defaultdict(set)
        self.outgoing_nodes = defaultdict(set)
        self._decay_factor = 1.0
        self.max_iterations = 100
        self.bidirectional = False
        self.sizes = {}
        self.nodes_set = set()

        for edge in edges:
            self.update_edge(edge, 1.0)

    def update_edge(
        self, 
        edge: Edge,
        weight: float, 
    ):
        self.nodes_set.add(edge.start)
        self.nodes_set.add(edge.end)
        # There can be multiple edges between the same nodes
        # in a case where two patterns with the same concept
        # have the same node at different positions.
        # Alternative solution is to add a second index to the edge
        if edge.start in self.incoming_nodes[edge.end]:
            # TODO: we need to remove the edge and add it again
            return
        # if start in self.incoming_nodes[end]:
        #     self._remove_edge(start, end)
            
        # if weight == 0:
        #     return

        priority_weight = -weight / self._decay_factor
        bisect.insort(self.priority_queues[edge.start], (priority_weight, edge))
        self.incoming_nodes[edge.end].add(edge.start)

        reverse_edge = edge.reverse()
        bisect.insort(self.reverse_priority_queues[reverse_edge.start], (priority_weight, reverse_edge))
        self.outgoing_nodes[reverse_edge.end].add(reverse_edge.start)
 
        # TODO: is index going to be changed??
        # if self.bidirectional:
        #     bisect.insort(self.priority_queues[end], (priority_weight, start, index))
        #     self.incoming_nodes[start].add(end)

    def lookup(
        self, 
        *nodes,
        indices: list[int], 
        weights: Optional[list[float]] = None, 
        depth: int = 1, 
        depth_decay: dict[str, float] = None,
        index_mismatch_penalty = 0.5,
        energy_map: Optional[NodeEnergyMap] = None,
        result_edge_types: Optional[set[str]] = None,
        transition_edge_types: Optional[set[str]] = None,
    ):
        true_pattern_match = [
            True for _ in range(len(nodes))
        ]

        if weights is None:
            weights = [1] * len(nodes)

        if depth_decay is None:
            depth_decay = {}
        
        initial_nodes = set(nodes)
        
        result = defaultdict(float)

        if energy_map is None:
            energy_map = NodeEnergyMap(self)
        
        for _ in range(depth):
            new_nodes = []
            new_weights = []
            new_indices = []
            new_true_pattern_match = []

            for node, input_index, input_weight, is_true_pm in zip(nodes, indices, weights, true_pattern_match):
                pq = self.priority_queues[node]
                iteration_limit = min(self.max_iterations, len(pq))

                for i in range(iteration_limit):
                    association_weight, edge = pq[i]

                    energy = 1 + energy_map.get_energy(edge.end)
                    weight = -association_weight * input_weight * energy
                    if edge.type_name in result_edge_types:
                        if edge.index != -1 and edge.index != input_index:
                            index_mismatch_size = abs(edge.index - input_index)
                            mismatch_multiplier = (1 - index_mismatch_penalty) ** index_mismatch_size
                            if input_index == 0 or edge.index == 0:
                                # we require the first index of the pattern to match
                                # but don't skip the node propagation, 
                                # since this pattern can be a transition
                                mismatch_multiplier = 0.0
                        else:
                            mismatch_multiplier = 1.0

                        if is_true_pm is False:
                            mismatch_multiplier *= 0.5

                        result[edge.end] += weight * mismatch_multiplier / self.sizes[edge.end]

                    if edge.type_name in transition_edge_types:
                        new_nodes.append(edge.end)
                        _depth_decay = depth_decay.get(edge.type_name, 0.0)
                        new_weights.append(input_weight * (1 - _depth_decay))
                        new_indices.append(input_index)
                        new_true_pattern_match.append(is_true_pm and edge.type_name != 'pattern')

            nodes = new_nodes
            weights = new_weights
            indices = new_indices
            true_pattern_match = new_true_pattern_match

        return [
            (x[0], round(x[1] - x[1] * (1 - self._decay_factor), 3))
            for x in sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]
            if x[0] not in initial_nodes
        ]

    def get_ws_data(self):
        pass
