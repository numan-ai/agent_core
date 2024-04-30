import copy
from src.base_module import AgentModule
from src.world_model.wm_entities import (
    InstanceFieldReference,
    InstanceReference,
    WorldModelEdge, 
    WorldModelNode,
    InstanceField,
)

from grass import AssociativeGraph


class WorldModel(AgentModule):
    def __init__(self, core) -> None:
        super().__init__(core)
        self.nodes = []
        self.edges: list[WorldModelEdge] = []
        self.associative_graph = AssociativeGraph([], bidirectional=False)

        self.node_by_id = {}
        
    def get_instance(self, node_id: str) -> 'Instance':
        from src.world_model.instance import Instance
        
        try:
            node = self.node_by_id[node_id]
            if not isinstance(node, Instance):
                raise ValueError("Fields must never be accessed this way, use get_node")
            return node
        except KeyError:
            raise ValueError(f"Instance with id {node_id} not found")
        
    def get_node(self, node_id: str) -> WorldModelNode:
        try:
            return self.node_by_id[node_id]
        except KeyError:
            raise ValueError(f"Node with id {node_id} not found")
        
    def add(self, instance: 'Instance'):
        from src.world_model.instance import Instance
        
        self.associative_graph.set_weight(
            instance.concept_name,
            instance.id,
            weight=1,
        )
        self.associative_graph.decay(1.01)
        
        if instance.world_model is self:
            return
        
        if instance.world_model is not None and instance.world_model is not self:
            raise ValueError("Instance is already assigned to another world model") 
        
        instance.world_model = self
        
        self.nodes.append(instance)
        self.node_by_id[instance.id] = instance
        
        props = instance.get_properties()
        
        for key, value in list(props.items()):
            if isinstance(value, InstanceReference):
                props[key] = self.get_instance(value.instance_id)
            elif isinstance(value, InstanceFieldReference):
                props[key] = self.get_instance(value.instance_id).get_field(value.field_name)
                
        for key, value in list(props.items()):
            field = self.create_field(instance.id, key)
            if isinstance(value, Instance):
                self.add(value)
                self.create_edge(field.id, value.id, "__value__")
            elif isinstance(value, InstanceField):
                self.create_edge(field.id, value.id, "__value__")
            else:
                field.value = value
                
        props.clear()
        
        return instance
    
    def get_out_field_node(self, instance_id: str, field_name: str) -> 'InstanceField':
        """ Returns InstanceField for a given instance and field name
        Instance -> InstanceField -> Instance
        """
        for edge in self.edges:
            if edge.start == instance_id and edge.name == field_name:
                return self.node_by_id[edge.end]
    
    def get_instance_field_instance(self, field_id: str) -> 'Instance':
        for edge in self.edges:
            if edge.end == field_id:
                return self.node_by_id[edge.start]
        
        raise ValueError(f"InstanceField {field_id} has no value")

    def get_inverse_fields(self, instance_id: str) -> list[tuple['Instance', 'InstanceField']]:
        fields = [
            self.node_by_id[edge.start]
            for edge in self.edges
            if edge.end == instance_id
        ]
        instances = [
            self.get_instance_field_instance(field.id)
            for field in fields
        ]
    
        return list(zip(instances, fields))
        
    def create_field(self, instance_id: str, name: str) -> 'InstanceField':
        field = InstanceField(name, self)
        self.nodes.append(field)
        self.node_by_id[field.id] = field
        self.create_edge(instance_id, field.id, name)
        
        return field
        
    def create_edge(self, start: str, end: str, edge_name: str):
        edge = WorldModelEdge(start, end, edge_name)
        self.edges.append(edge)
        return edge
        
    def out_one(self, node_id: str, edge_name: str):
        for edge in self.edges:
            if edge.start == node_id and edge.name == edge_name:
                return self.node_by_id[edge.end]
            
    def in_one(self, node_id: str, edge_name: str):
        for edge in self.edges:
            if edge.end == node_id and edge.name == edge_name:
                return self.node_by_id[edge.start]
            
    def outgoing_edges(self, node_id: str, edge_name: str = None) -> list[WorldModelEdge]:
        return [
            edge for edge in self.edges 
            if edge.start == node_id and (edge_name is None or edge.name == edge_name)
        ]
    
    def incoming_edges(self, node_id: str, edge_name: str = None) -> list[WorldModelEdge]:
        return [
            edge for edge in self.edges 
            if edge.end == node_id and (edge_name is None or edge.name == edge_name)
        ]
        
    def both_edges(self, node_id: str, edge_name: str = None) -> list[WorldModelEdge]:
        return [
            edge for edge in self.edges 
            if (edge.end == node_id or edge.start == node_id) and (
                edge_name is None or edge.name == edge_name)
        ]
    
    def remove_out_edges(self, node_id: str, name: str):
        self.edges = [
            edge for edge in self.edges
            if not (edge.start == node_id and edge.name == name)
        ]
            
    def copy(self):
        new_world = WorldModel(self.core)
        for node in self.nodes:
            node_copy = node.copy()
            node_copy.world_model = new_world
            new_world.nodes.append(node_copy)
            new_world.node_by_id[node_copy.id] = node_copy
            
        new_world.edges = copy.deepcopy(self.edges)
            
        return new_world
