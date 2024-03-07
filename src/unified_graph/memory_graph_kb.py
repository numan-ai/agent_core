class MemoryGraphKb:
    """ Implements graph knowledge base in memory.
    Functions:
    - create node (with data or without)
    - create edge (with data or without)
    - get node by id
    - get edge by id
    - get outgoing edges from node
    - get incoming edges to node
    - find nodes by label and property
    """
    
    def __init__(self):
        self.nodes: dict[int, KBNode] = {}
        self.edges: dict[int, KBEdge] = {}
        self.next_node_id = 0
        self.next_edge_id = 0
        
    def load(self, data: list):
        id_map = {}
        edges = []
        for node in data:
            kb_node = self.create_node(node['label'], node.get('data', {}))
            id_map[node['id']] = kb_node.id
            edges.extend([
                (node['id'], edge[0], edge[1]) for edge in node.get('edges', [])
            ])
        
        for edge in edges:
            self.create_edge(edge[1], id_map[edge[0]], id_map[edge[2]])
        
    def create_node(self, label: str, data: dict = None) -> KBNode:
        node_id = self.next_node_id
        self.next_node_id += 1
        node = KBNode(node_id, label, data or {}, {})
        self.nodes[node_id] = node
        return node
    
    def create_edge(self, label: str, start_id: int, end_id: int, data: dict = None) -> KBEdge:
        edge_id = self.next_edge_id
        self.next_edge_id += 1
        edge = KBEdge(edge_id, label, start_id, end_id, data or {})
        self.edges[edge_id] = edge
        return edge
    
    def get_node(self, node_id: int) -> KBNode:
        return self.nodes[node_id]
    
    def get_edge(self, edge_id: int) -> KBEdge:
        return self.edges[edge_id]
    
    def get_outgoing_edges(self, node_id: int, edge_label: str = None) -> list[KBEdge]:
        return [
            edge for edge in self.edges.values()
            if edge.start_id == node_id and (edge_label is None or edge.label == edge_label)
        ]
        
    def get_incoming_edges(self, node_id: int, edge_label: str = None) -> list[KBEdge]:
        return [
            edge for edge in self.edges.values()
            if edge.end_id == node_id and (edge_label is None or edge.label == edge_label)
        ]
        
    def find_nodes(self, label: str, key: str, value: any) -> list[KBNode]:
        return [
            node for node in self.nodes.values()
            if node.label.split('__')[0] == label and node.data.get(key) == value
        ]
