import bisect
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Hashable, Optional

from src.knowledge_base.hierarchy import DictHierarchy


@dataclass
class Pattern:
    concept: str
    nodes: list[str]


sentence = [
    "Word_my", "Word_brother", "Word_is", "Word_running",
    # "Word_my", "Word_brother", "Word_is", "Word_far",
]

patterns = [
    Pattern("LivingEntityIsDoingProcess", [
        "LivingEntity", "IsDoing", "Process"
    ]),
    Pattern("NonLivingEntityIsDoingProcess", [
        "NonLivingEntity", "IsDoing", "Process"
    ]),
    Pattern("NonLivingEntityIsBeingActivity", [
        "NonLivingEntity", "IsBeing", "Activity"
    ]),
    Pattern("NonLivingEntityIsBeingFar", [
        "NonLivingEntity", "IsBeing", "DistanceFar"
    ]),
    Pattern("LivingEntityIsBeingFar", [
        "LivingEntity", "IsBeing", "DistanceFar"
    ]),
    Pattern("NonLivingEntity", [
        "PossessivePronoun", "Hobby"
    ]),
    Pattern("LivingEntity", [
        "PossessivePronoun", "RelativeBrother"
    ]),
    Pattern("NonLivingEntity", [
        "PossessivePronoun", "Home"
    ]),
    # Pattern("P1", ["A", "B", "C"]),
    # Pattern("P2", ["C", "A", "B"]),
]

word_concepts = {
    "Word_my": ["PossessivePronoun"],
    "Word_hobby": ["Hobby"],
    "Word_brother": ["RelativeBrother"],
    "Word_home": ["Home"],
    "Word_is": ["IsBeing", "IsDoing"],
    "Word_running": ["Activity", "Process"],
    "Word_far": ["DistanceFar"],
}

for _word, _concepts in word_concepts.items():
    for _concept in _concepts:
        patterns.append(Pattern(_concept, [_word, ]))



for pattern in patterns:
    # add tails to patterns
    # empty string represents the end of the pattern
    pattern.nodes.append("")

pattern_map = {
    pattern.concept: pattern
    for pattern in patterns
}

hierarchy = DictHierarchy(children={
    "Activity": ["ActivityRunning"],
    "Process": ["ProcessRunning"],
    "LivingEntity": ["RelativeBrother", ],
    # "A": ["A1"],
    # "B": ["B1"],
    # "C": ["C1"],
    # "C1": ["C2"],
})


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


class NodeEnergyMap:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.energies = defaultdict(float)

    def add_energy(self, node: Hashable, energy: float, decay: float = 0.75):
        self.energies[node] += energy
        # TODO: propage energy to the connected nodes

    def get_energy(self, node: Hashable):
        return self.energies[node]


class Graph:
    def __init__(self, edges: list[Edge]) -> None:
        self.priority_queues: dict[list[tuple[float, Edge]]] = defaultdict(list)
        self.incoming_nodes = defaultdict(set)
        self._decay_factor = 1.0
        self.max_iterations = 100
        self.bidirectional = False

        for edge in edges:
            self.update_edge(edge, 1.0)

    def update_edge(
        self, 
        edge: Edge,
        weight: float, 
    ):
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
        depth_decay: float = 0.5,
        index_mismatch_penalty = 0.5,
        energy_map: Optional[NodeEnergyMap] = None,
        result_edge_types: Optional[set[str]] = None,
        transition_edge_types: Optional[set[str]] = None,
    ):
        if weights is None:
            weights = [1] * len(nodes)
        
        initial_nodes = set(nodes)
        
        result = defaultdict(float)

        if energy_map is None:
            energy_map = NodeEnergyMap(self)
        
        for _ in range(depth):
            new_nodes = []
            new_weights = []
            new_indices = []

            for node, input_index, input_weight in zip(nodes, indices, weights):
                pq = self.priority_queues[node]
                iteration_limit = min(self.max_iterations, len(pq))

                for i in range(iteration_limit):
                    association_weight, edge = pq[i]

                    energy = 1 + energy_map.get_energy(edge.end)
                    weight = -association_weight * input_weight * energy
                    if edge.type_name in result_edge_types:
                        if edge.index != -1 and edge.index != input_index:
                            index_mismatch_size = abs(edge.index - input_index)
                            mismatch_multiplier = index_mismatch_penalty ** index_mismatch_size
                        else:
                            mismatch_multiplier = 1.0
                        result[edge.end] += weight * mismatch_multiplier
                    
                    if edge.type_name in transition_edge_types:
                        transition_multiplier = 1.0
                        if edge.type_name == "pattern":
                            transition_multiplier = 0.5
                        new_nodes.append(edge.end)
                        new_weights.append(weight * (1 - depth_decay) * transition_multiplier)
                        new_indices.append(input_index)
                    
            nodes = new_nodes
            weights = new_weights
            indices = new_indices

        return [
            (x[0], round(x[1] - x[1] * (1 - self._decay_factor), 3))
            for x in sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]
            if x[0] not in initial_nodes
        ]


g = Graph([
    Edge(node, pattern.concept, "pattern", i)
    for pattern in patterns
    for i, node in enumerate(pattern.nodes)
] + [
    Edge(child, parent, "parent", -1)
    for parent, children in hierarchy.children.items()
    for child in children
])

energy_map = NodeEnergyMap(g)
energy_map.add_energy("P2", 1.0)


@dataclass
class Match:
    layer_idx: int
    size: int = 1
    concept: Optional[str] = None
    children: list["Match"] = field(default_factory=list, repr=False)


class Tree:
    def __init__(self) -> None:
        self.layers = [[], [], [], []]
        self.call_stack = []

    def add_word(self, word: str):
        for idx, layer in enumerate(self.layers):
            layer.append(Match(layer_idx=idx))
        match = self.layers[0][-1]
        match.concept = word

    def match(self, idx, size, is_end: bool = False):
        print("Matching", idx, size, "end" if is_end else "")

        if idx + size + 1 > len(self.layers[0]):
            return

        matches = []
        concepts = []
        indices = []

        current_idx = idx

        while current_idx <= idx + size:
            for layer in reversed(self.layers):
                match = layer[current_idx]
                if match.concept is None:
                    continue
                matches.append(match)
                concepts.append(match.concept)
                current_idx += match.size
                break

        if is_end:
            concepts.append("")

        indices = list(range(len(concepts)))

        res = g.lookup(
            *concepts,
            indices=indices,
            depth=5,
            depth_decay=0.0,
            energy_map=energy_map,
            index_mismatch_penalty=0.5,
            result_edge_types={"pattern", },
            transition_edge_types={"parent", "pattern"},
        )

        print('concepts', concepts)
        print('found', res[:3])
        breakpoint()

        pattern_name = res[0][0]
        pattern_nodes = pattern_map[pattern_name].nodes

        new_idx = idx
        for match, node in zip(matches, pattern_nodes):
            if match.concept != node:
                print('not equal!!')
                # on unsuccessful match go try matching further
                # and then come back
                # new_idx = idx + matches[0].size
                self.call_stack.append((idx, size))
                self.match(new_idx, 0, is_end=False)
            new_idx += match.size

        if len(pattern_nodes) - 1 > len(matches):
            # we are not ready to match this
            new_size = sum([
                match.size
                for match in matches
            ])
            print("Expanding match")
            self.match(idx, new_size)
            return
        
        new_layer = max([
            match.layer_idx
            for match in matches
        ]) + 1

        if len(matches) == len(pattern_nodes) - 1:
            self.layers[new_layer][idx].concept = pattern_name
            self.layers[new_layer][idx].children = matches
            self.layers[new_layer][idx].size = sum([
                match.size
                for match in matches
            ])
            if self.call_stack:
                print("Sucess, returning back")
                new_idx, new_size = self.call_stack.pop()
                self.match(new_idx, new_size, is_end=False)
                breakpoint()
                pass

            print("Sucess, try expanding up")
            # on successful match go up+forward
            self.match(idx, size, is_end=False)

        breakpoint()
        pass


tree = Tree()
tree.add_word(sentence[0])
tree.add_word(sentence[1])
tree.add_word(sentence[2])
tree.add_word(sentence[3])
tree.match(0, 0, is_end=False)
