import copy
import random
import uuid

from typing import Optional
from dataclasses import dataclass, field


FIELD_VALUE_EMPTY = object()


class WorldModelNode:
    def __init__(self, *, instance_id=None):
        self.id = instance_id or str(uuid.uuid4())


@dataclass
class WorldModelEdge:
    start: str
    end: str
    name: str


class WorldModel:
    def __init__(self) -> None:
        self.nodes = []
        self.edges: list[WorldModelEdge] = []
        
        self.node_by_id = {}
        
    def get_instance(self, node_id: str) -> 'Instance':
        try:
            node = self.node_by_id[node_id]
            if not isinstance(node, Instance):
                raise ValueError("Fields must never be accessed directly, use relations")
            return node
        except KeyError:
            raise ValueError(f"Instance with id {node_id} not found")
        
    def add(self, instance: 'Instance'):
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
                self.create_edge(field.id, value.id, "value")
            elif isinstance(value, InstanceField):
                self.create_edge(field.id, value.id, "value")
            else:
                field.value = value
                
        props.clear()
        
        return instance
        
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
            
    def outgoing_edges(self, node_id: str) -> list[WorldModelEdge]:
        return [edge for edge in self.edges if edge.start == node_id]
    
    def incoming_edges(self, node_id: str) -> list[WorldModelEdge]:
        return [edge for edge in self.edges if edge.end == node_id]
            
    def copy(self):
        new_world = WorldModel()
        for node in self.nodes:
            node_copy = node.copy()
            new_world.add(node_copy)
            
        new_world.edges = copy.deepcopy(self.edges)
            
        return new_world


class Instance(WorldModelNode):
    """
    If the instance is assigned to a world model, then properties
    only store constant field values, and relations are stored in the world model.
    Fields = Properties + Relations.
    Properties = Fields for instances without world model.
    """
    def __init__(self, concept_name: str, fields: dict[str, any], *, instance_id=None):
        super().__init__(instance_id=instance_id)
        self.concept_name = concept_name
        self.__properties = fields
        self.world_model: Optional[WorldModel] = None
        self.fields = InstanceFieldsView(self)
    
    def change_world_model(self, world_model: WorldModel):
        if self.world_model is None:
            raise ValueError("Instance is not assigned to a world model")
        self.world_model = world_model
            
    def get_properties(self):
        return self.__properties
    
    def get_field(self, name):
        field = self.world_model.out_one(self.id, name)
        if field is None:
            raise AttributeError(f"Instance {self} has no attribute {name}")
        
        return field
    
    def __repr__(self) -> str:
        return f"{self.concept_name}({self.__properties})"


class InstanceFieldsView:
    """ Aggregates fields and relations of the instance """
    def __init__(self, instance: Instance):
        self._instance: Instance = instance
        self._properties = instance.get_properties()
        
    def __getattr__(self, name: str):
        if name in self._properties:
            return self._properties[name]
        
        if not self._instance.world_model:
            raise AttributeError(f"Instance {self._instance} has no attribute {name}")
        
        field: InstanceField = self._instance.world_model.out_one(
            self._instance.id, name)
        
        if field is None:
            raise AttributeError(f"Instance {self._instance} has no attribute {name}")
        
        if field.value is not FIELD_VALUE_EMPTY:
            return field.value
        
        value = self._instance.world_model.out_one(field.id, "value")
        
        if value is None:
            raise AttributeError(f"Instance {self._instance} has no attribute {name}")
        
        return value

    def __setattr__(self, name: str, value: any):
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        if isinstance(value, Instance):
            if self._instance.world_model is None:
                raise ValueError("Instance is not assigned to a world model")
            
            self._instance.world_model.create_edge(self._instance, value, name)
        else:
            self._properties[name] = value

    def __getitem__(self, name: str):
        return self.__getattr__(name)
    
    def __setitem__(self, name: str, value: any):
        return self.__setattr__(name, value)

    def __repr__(self) -> str:
        return repr(self._properties)


class InstanceField(WorldModelNode):
    def __init__(self, name, world_model) -> None:
        super().__init__()
        self.name = name
        self.world_model = world_model
        self._value = FIELD_VALUE_EMPTY
        
    @property
    def value(self):
        if self._value is FIELD_VALUE_EMPTY:
            return self.world_model.out_one(self.id, "value")
        return self._value
    
    @value.setter
    def value(self, value):
        assert not isinstance(value, WorldModelNode)
        self._value = value
        
    def __repr__(self) -> str:
        if self._value is FIELD_VALUE_EMPTY:
            return f"<Field {self.name}>"
        return f"<Field {self.name}=[{self._value}]>"


@dataclass
class InstanceReference:
    instance_id: str
    
    
@dataclass
class InstanceFieldReference:
    instance_id: str
    field_name: str


def press_button_a(world_model):
    world_model.get_instance("Counter-1").fields.value += 1
    
    
def press_button_b(world_model):
    world_model.get_instance("Counter-1").fields.value -= 3


def is_numeric_equality_goal_reached(goal):
    target_value = goal.fields.target_value.value
    current_value = goal.fields.value_to_change.value
    
    return target_value == current_value


def get_numeric_equality_goal_closeness(goal):
    target_value = goal.fields.target_value.value
    current_value = goal.fields.value_to_change.value
    
    return abs(target_value - current_value)


def find_the_next_action_using_associations_only(goal):
    return random.choice([press_button_a, press_button_b])


def apply_action(world_model, action):
    world_model = world_model.copy()
    action(world_model)
    return world_model


def is_closer_to_the_goal(goal_closeness, new_goal_closeness):
    return new_goal_closeness < goal_closeness


def simple_planning_strategy(goal):
    goal_closeness = get_numeric_equality_goal_closeness(goal)
    
    world_model = goal.world_model
    
    while not is_numeric_equality_goal_reached(goal):
        next_action = find_the_next_action_using_associations_only(goal)
        new_world_copy = apply_action(world_model, next_action)
        goal.change_world_model(new_world_copy)
        
        new_goal_closeness = get_numeric_equality_goal_closeness(goal)
        goal.change_world_model(world_model)
        
        if is_closer_to_the_goal(goal_closeness, new_goal_closeness):
            goal_closeness = new_goal_closeness
            world_model = new_world_copy
            goal.change_world_model(world_model)
            print(f"New goal closeness: {new_goal_closeness}, {next_action.__name__}")
        else:
            print(f"Bad action: {next_action.__name__}")


def main():
    wm = WorldModel()

    wm.add(Instance("TargetDisplay", {
        "value": 7,
    }, instance_id="TargetDisplay-1"))
    
    wm.add(Instance("Counter", {
        "value": 0,
    }, instance_id="Counter-1"))

    goal = wm.add(Instance("MakeValueEqualTo", {
        "value_to_change": InstanceFieldReference("Counter-1", "value"),
        "target_value": InstanceFieldReference("TargetDisplay-1", "value"),
    }))
    
    logic = Instance("IAddInstruction", {
        "instance": InstanceFieldReference("Counter-1", "value"),
        "value": 1,
    }, instance_id="IAddInstruction-1")
    
    btn = wm.add(Instance("ButtonA", {
        "logic_on_press": logic
    }))
    
    simple_planning_strategy(goal)
    
    
if __name__ == "__main__":
    main()
