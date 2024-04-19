import copy
import heapq
import random
from dataclasses import (
    field,
    dataclass,
)

import agci

from src.knowledge_base.hierarchy import DictHierarchy
from src.knowledge_base.module import (
    KBEdgeType, 
    KBNodeType, 
    KnowledgeBase,
    KBEdgeDirection,
)


@dataclass(order=True)
class Node:
    energy: float
    node_id: str = field(compare=False)
    edges: list = field(default_factory=list, compare=False, repr=False)


class Graph:
    def __init__(self, lookup_concept, hierarchy):
        self.lookup_concept = lookup_concept
        self.hierarchy = hierarchy
        self.nodes = {}
        self.max_heap = []
        self.updated_nodes = set()
        self.decay_factor = 1.0
        
    def add_node(self, node_id):
        if node_id not in self.nodes:
            node = Node(0, node_id)
            self.nodes[node_id] = node
            if self.hierarchy.is_subconcept(node_id, self.lookup_concept):
                heapq.heappush(self.max_heap, node)
            
    def set_weight(self, start, end, weight, bidirectional=True):
        if start not in self.nodes:
            self.add_node(start)
        
        if end not in self.nodes:
            self.add_node(end)
        
        # remove the edge if it exists
        self.nodes[start].edges = [(n, w) for n, w in self.nodes[start].edges if n != end]
        
        self.nodes[start].edges.append((end, weight))
        
        if bidirectional:
            self.nodes[end].edges.append((start, weight))
            
    def decay(self, factor: float):
        """ Positive factor increases the decay, negative decreases it. 
        This is a percentage-based decay - factor 0.1 means 10% decay.
        """
        self.decay_factor *= 1 - factor

    def add_energy(self, node_id, energy):
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist in the graph")
        
        self._propagate_energy(node_id, energy / self.decay_factor, 0)
        self._update_heap()

    def _propagate_energy(self, node_id, energy, depth):
        if node_id in self.updated_nodes:
            return
        if depth > 5 or energy < 0.005:
            return

        self._update_energy(node_id, energy)
        
        node = self.nodes[node_id]
        self.updated_nodes.add(node_id)
        for (neighbor, weight) in node.edges:
            self._propagate_energy(neighbor, energy * weight, depth + 1)

    def _update_energy(self, node_id, energy_diff):
        node = self.nodes[node_id]
        new_node = copy.deepcopy(node)
        node.energy = -float('inf')
        self.nodes[node_id] = new_node
        new_node.energy += energy_diff

    def _update_heap(self):
        for node_id in self.updated_nodes:
            node = self.nodes[node_id]
            if self.hierarchy.is_subconcept(node_id, self.lookup_concept):
                heapq.heappush(self.max_heap, node)
        self.updated_nodes.clear()

    def find_max_energy_node(self):
        # TODO: use heapq.heappop instead of nlargest
        return heapq.nlargest(1, self.max_heap)[0]


CODE = """
def Task__delete_folder():
    print('f1: 1')
    print('f1: 2')
    print('f1: 3')
    print('f1: 4')
    print('f1: 5')
    print('f1: 6')
    print('f1: 7')
    print('f1: 8')
    print('f1: 9')
    print('f1: 10')
    print('f1: 11')
    
    
def Task__print_expression():
    print('f2: @')
"""


def main():
    kb = KnowledgeBase(None)
    tasks = kb.find_nodes(KBNodeType.TASK, ())
    
    interpreter = agci.StepInterpreter({
        'print': print,
    })
    interpreter.load_code(CODE)
    
    hierarchy = DictHierarchy(children={
        "Task": [
            f"Task__{task.data['name']}" for task in tasks    
        ],
    })
    
    graph = Graph("Task", hierarchy)
    for task in tasks:
        task_concept_name = f"Task__{task.data['name']}"
        concepts = kb.out(task.id, KBEdgeType.TASK, direction=KBEdgeDirection.IN)
        for concept in concepts:
            concept_name = concept.data['name']
            # print(concept_name)
            graph.set_weight(concept_name, task_concept_name, 0.5)
    
    graph.add_energy("DeleteFolder", 0.1)
    
    task = graph.find_max_energy_node()
    interpreter.trigger_function(task.node_id)
    current_func = task.node_id
    
    while True:
        interpreter.step()
        
        if random.random() > 0.97:
            graph.add_energy("PrintMathExpression", 0.1)
        
        graph.decay(0.001)
        
        task = graph.find_max_energy_node()
        if task.node_id != current_func:
            # Increase the energy of the current function
            #   in order to avoid rapid switching between functions
            graph.add_energy(task.node_id, 0.1)
            interpreter.trigger_function(task.node_id)
            current_func = task.node_id
    

if __name__ == "__main__":
    main()
