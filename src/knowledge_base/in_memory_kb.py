from typing import Optional
from src.knowledge_base.module import (
    KBNode,
    KBEdge,
    KBEdgeType,
    KBNodeType,
    KBEdgeDirection,
    BaseKnowledgeBase,
)


class InMemoryKB(BaseKnowledgeBase):
    def __init__(self, nodes: list[dict], edges: list[tuple[int, int, str]]):
        self.nodes = {}
        for node in nodes:
            if node['id'] in self.nodes:
                raise ValueError(f"Duplicate node id: {node['id']}")
            self.nodes[node['id']] = node
        
        self.edges = edges
        self.next_id = max([node['id'] for node in nodes], default=0) + 1
        
    def out(self, node_id: int, edge_type: KBEdgeType, 
            edge_filters: tuple = None, direction: KBEdgeDirection = KBEdgeDirection.OUT, 
            direct=True) -> list[KBNode]:
        result = []
        
        for start_id, end_id, edge_name in self.edges:
            if direction is KBEdgeDirection.IN:
                start_id, end_id = end_id, start_id
            
            if direction is KBEdgeDirection.ANY and end_id == node_id:
                start_id, end_id = end_id, start_id
                
            if start_id != node_id:
                continue
            
            if edge_name is not edge_type:
                continue
            
            node = self.nodes[end_id]
            result.append(KBNode(**node))
            
        return result
    
    def out_dict(self, node_id: int, edge_type: KBEdgeType, 
                 edge_filters: tuple, key: str, direction: KBEdgeDirection, 
                 direct=True) -> dict[str, KBNode]:
        pass
    
    def out_dict2(self, node_id: int, edge_type: KBEdgeType, 
                  edge_filters: tuple = None, key: str = 'name', direction: KBEdgeDirection = KBEdgeDirection.OUT, 
                  direct=True) -> dict[str, KBNode]:
        result = {}
        
        for start_id, end_id, edge_name in self.edges:
            if start_id != node_id:
                continue
            
            if edge_name is not edge_type:
                continue
            
            node = self.nodes[end_id]
            result[node['data'][key]] = KBNode(**node)
            
        return result
    
    def find_nodes(self, node_type: KBNodeType, filters: tuple) -> list[KBNode]:
        result = []
        
        for node in self.nodes.values():
            if node['label'] != node_type.value:
                continue
            
            for key, value in filters:
                if node['data'].get(key) != value:
                    break
            else:
                result.append(node)
                
        return [
            KBNode(**node) for node in result   
        ]
                

    def get_node(self, node_id: int) -> KBNode:
        pass
    
    def new_node(self, label: str, data: dict) -> KBNode:
        pass
    
    def new_edge(self, label: str, start_node_id: int, end_node_id: int, data: dict) -> KBEdge:
        pass
    
    def _iterate_hierarchy_up(self, concept_id: int, already_visited: set[int] = None):
        if already_visited is None:
            already_visited = set()
                        
        if concept_id in already_visited:
            return
            
        already_visited.add(concept_id)
        
        yield concept_id
        
        parents = []
        
        for edge in self.edges:
            if edge[0] == concept_id and edge[2] is KBEdgeType.PARENT:
                yield edge[0]
                parents.append(edge[1])
                
        for parent in parents:
            yield from self._iterate_hierarchy_up(parent)

    def get_field(self, concept_id: int, field_name: str) -> Optional[KBNode]:
        for parent_id in self._iterate_hierarchy_up(concept_id):
            for edge in self.edges:
                if edge[0] == parent_id and edge[2] is KBEdgeType.FIELD_NODE:
                    field = self.nodes[edge[1]]
                    if field['data']['name'] == field_name:
                        return KBNode(**field)
