from dataclasses import dataclass, field
from uuid import uuid4
from typing import Optional

@dataclass
class Node:
    name: str
    node_type: Optional[str] = "object"
    id: Optional[any] = field(default_factory=lambda:str(uuid4()))
    value: Optional[bool] = False  # For attributes
    position: Optional[tuple[int, int]] = (500, 500)  # Only relevant graphical attribute

@dataclass
class Edge:
    from_id: int
    to_id: int
    name: Optional[str] = ""
    id: Optional[any] = field(default_factory=lambda:str(uuid4()))
    

class Graph:
    def __init__(self, nodes: list[Node], edges: list[Edge]):
        self.nodes = nodes
        self.edges = edges

    def node_out_edges(self, node_id: int) -> list[Edge]:
        out = []
        for edge in self.edges:
            if edge.from_id == node_id:
                out.append(edge)
        return out
    
    def node_in_edges(self, node_id: int) -> list[Edge]:
        out = []
        for edge in self.edges:
            if edge.to_id == node_id:
                out.append(edge)
        return out
    
    def get_node_by_name(self, node_name: str) -> Node:
        for node in self.nodes:
            if node.name == node_name:
                return node
            
    def get_node_by_id(self, node_id: int) -> Node:
        for node in self.nodes:
            if node.id == node_id:
                return node

    def organize_in_layers(self, reverse=False) -> list[list[Edge]]:
        out = []
        temporal_nodes = self.nodes.copy()
        temporal_edges = self.edges.copy()

        while temporal_nodes:
            newest_layer = []
            for node in temporal_nodes:
                if not self.node_in_edges(node.id, temporal_edges):
                    newest_layer.append(node)
            if reverse:
                out.append(newest_layer)
            else:
                out.insert(0,newest_layer)
            for node in newest_layer:
                temporal_nodes.remove(node)
                for edge in self.node_out_edges(node.id, temporal_edges):
                    temporal_edges.remove(edge)
        return out
    
if __name__ == "__main__":
    nodes = [
        Node("A0"), Node("A1"), Node("A2"),
        Node("B0"), Node("B1"),
        Node("C0"),
        Node("D0"), Node("D1"),
        Node("E0"), Node("E1"), Node("E2"), Node("E3")
    ]

    edges = [
        Edge(8, 0), Edge(6, 0), Edge(3, 1),
        Edge(10, 2), Edge(6, 3), Edge(7, 3),
        Edge(5, 3), Edge(5, 4), Edge(7, 5),
        Edge(9, 6), Edge(11, 7), Edge(4, 2)
    ]

    graph = Graph(nodes, edges)

    [print(a) for a in graph.organize_in_layers()]