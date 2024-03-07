from src.knowledge_base.module import BaseKnowledgeBase, KBEdge, KBEdgeDirection, KBEdgeType, KBNode, KBNodeType


class InMemoryKB(BaseKnowledgeBase):
    def __init__(self, nodes: list[dict], edges: list[tuple[int, int, str]]):
        self.nodes = {}
        for node in nodes:
            if node['id'] in self.nodes:
                raise ValueError(f"Duplicate node id: {node['id']}")
            self.nodes[node['id']] = node
        
        self.edges = edges
        self.next_id = max([node['id'] for node in nodes]) + 1
        
    def out(self, node_id: int, edge_type: KBEdgeType, 
            edge_filters: tuple = None, direction: KBEdgeDirection = KBEdgeDirection.OUT, 
            direct=True) -> list[KBNode]:
        pass
    
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
            result[node['data'][key]] = KBNode(**node, metadata={})
            
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
            KBNode(**node, metadata={}) for node in result   
        ]
                

    def get_node(self, node_id: int) -> KBNode:
        pass
    
    def new_node(self, label: str, data: dict) -> KBNode:
        pass
    
    def new_edge(self, label: str, start_node_id: int, end_node_id: int, data: dict) -> KBEdge:
        pass
