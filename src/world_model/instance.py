from typing import Optional

from src.knowledge_base.concept import Concept
from src.world_model.module import WorldModel
from src.world_model.wm_entities import WorldModelNode


FIELD_VALUE_EMPTY = object()


class Instance(WorldModelNode):
    """
    If the instance is assigned to a world model, then properties
    only store constant field values, and relations are stored in the world model.
    Fields = Properties + Relations.
    Properties = Fields for instances without world model.
    """
    def __init__(self, concept_name: str, fields: dict[str, any] = None, *, instance_id=None):
        super().__init__(instance_id=instance_id)
        self.concept_name = concept_name
        self.__properties = fields or {}
        self.world_model: Optional[WorldModel] = None
        self.fields = InstanceFieldsView(self)
        self.out_fields = InstanceOutFieldsView(self)
    
    def change_world_model(self, world_model: WorldModel):
        if self.world_model is None:
            raise ValueError("Instance is not assigned to a world model")
        self.world_model = world_model
            
    def get_properties(self):
        return self.__properties
    
    def get_concept(self) -> Concept:
        if self.world_model is not None:
            # raise NotImplementedError()
            pass
        
        return Concept(self.concept_name, {
            field_name: field_value.get_concept()
            for field_name, field_value in self.__properties.items()
            if isinstance(field_value, Instance)
        })
    
    def get_field(self, name):
        field = self.world_model.out_one(self.id, name)
        if field is None:
            raise AttributeError(f"Instance {self} has no attribute {name}")
        
        return field
    
    def copy(self):
        return Instance(
            self.concept_name,
            {}, 
            instance_id=self.id)
    
    # def __repr__(self) -> str:
    #     return f"{self.concept_name}({self.__properties})"
    
    def __repr__(self, indent=0):
        indent_str = ' ' * indent
        field_indent_str = ' ' * (indent + 4)
        
        # Representing the name
        repr_str = f"{type(self).__name__}('{self.concept_name}'"

        fields = self.fields.get_all_fields()
        
        def _repr(value, idnt):
            if isinstance(value, Instance):
                if value.concept_name in ["String", "Number"]:
                    return f'{value.concept_name}({value.fields.value!r})'
                return value.__repr__(idnt + 4)
            elif isinstance(value, list):
                list_indent = '    ' * (idnt + 2)
                list_end_indent = '    ' * (idnt + 1)
                values_repr = ', '.join(_repr(v, idnt + 4) for v in value)
                return f"[\n{list_indent}{values_repr}\n{list_end_indent}]"
            else:
                return repr(value)
                
        # Representing the fields
        if fields:
            repr_str += ", {\n"
            for key, value in fields.items():
                field_repr = _repr(value, indent)
                repr_str += f"{field_indent_str}'{key}': {field_repr},\n"
            repr_str += f"{indent_str}}}"
        
        repr_str += ")"
        return repr_str

    def __eq__(self, other_instance: 'Instance'):
        if type(other_instance) == Instance:
            equal_names = self.concept_name == other_instance.concept_name
            equal_fields = self.__properties == other_instance.__properties
            return equal_names and equal_fields
        else: return False


class InstanceOutFieldsView:
    """ Aggregates parenting fields and relations of the instance """

    def __init__(self, instance: Instance):
        self._instance: Instance = instance

    def get(self):
        assert self._instance.world_model is not None
        return self._instance.world_model.get_inverse_fields(self._instance.id)


class InstanceFieldsView:
    """ Aggregates fields and relations of the instance """
    def __init__(self, instance: Instance):
        self._instance: Instance = instance
        self._properties = instance.get_properties()
        
    def get_all_fields(self):
        if not self._instance.world_model:
            return self._properties.copy()
        
        kb_fields = self._instance.world_model.outgoing_edges(self._instance.id)
        
        result = {}
        
        for field in kb_fields:
            result[field.name] = self._instance.world_model.get_node(field.end)
            
        return result
        
    def __getattr__(self, name: str):
        if name in self._properties:
            return self._properties[name]
        
        if not self._instance.world_model:
            breakpoint()
            raise AttributeError(f"Instance {self._instance} has no attribute '{name}'")
        
        field = self._instance.world_model.out_one(
            self._instance.id, name)
        
        if field is None:
            raise AttributeError(f"Instance {self._instance} has no attribute {name}")
        
        if field.value is not FIELD_VALUE_EMPTY:
            return field.value
        
        value = self._instance.world_model.out_one(field.id, "__value__")
        
        if value is None:
            raise AttributeError(f"Instance {self._instance} has no attribute {name}")
        
        return value

    def __setattr__(self, name: str, value: any):
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        wm = self._instance.world_model
        if wm is not None:
            # find the existing field
            field = wm.out_one(self._instance.id, name)
            if field is None:
                raise AttributeError(f"Instance {self._instance} has no attribute {name}")
                
            if isinstance(value, WorldModelNode):
                wm.add(value)
                # remove old __value__ edge
                wm.remove_out_edges(field.id, "__value__")
                # create a new __value__ edge
                wm.create_edge(field.id, value.id, "__value__")
            else:
                field.value = value
        else:
            self._properties[name] = value

    def __getitem__(self, name: str):
        return self.__getattr__(name)
    
    def __setitem__(self, name: str, value: any):
        return self.__setattr__(name, value)

    def __repr__(self) -> str:
        return repr(self._properties)


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


def find_action_concept_for_numeric_equality(goal):
    if goal.fields.target_value.value > goal.fields.value_to_change.value:
        return "Increase"
    elif goal.fields.target_value.value < goal.fields.value_to_change.value:
        return "Decrease"
    else:
        return "DoNothing"
    

def find_the_next_action_using_associations_only(goal):
    action_concept = find_action_concept_for_numeric_equality(goal)
    instance = goal.fields.value_to_change
    
    hierarchy = {
        "Increase": {"IAddInstruction", },
        "Decrease": {"ISubInstruction", },
    }
    
    wm = instance.world_model
    
    for edge in wm.outgoing_edges(instance.id):
        raise NotImplementedError()
    
    for edge in wm.incoming_edges(instance.id):
        if edge.name != '__value__':
            # skip own instance, only iterate external references
            continue
        start = wm.get_node(edge.start)
        assert isinstance(start, InstanceField)
        field_instance = wm.in_one(edge.start, start.name)
        if field_instance.concept_name in hierarchy[action_concept]:
            button_field_instance = wm.in_one(field_instance.id, '__value__')
            button_instance = wm.in_one(button_field_instance.id, button_field_instance.name)
            return globals()[button_instance.fields.simple_button_press]
        
    raise ValueError("No action found")


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
    
    wm.add(Instance("ButtonA", {
        "logic_on_press": Instance("IAddInstruction", {
            "instance": InstanceFieldReference("Counter-1", "value"),
            "value": 1,
        }, instance_id="IAddInstruction-1"),
        "simple_button_press": "press_button_a",
    }, instance_id="ButtonA-1"))
    
    wm.add(Instance("ButtonB", {
        "logic_on_press": Instance("ISubInstruction", {
            "instance": InstanceFieldReference("Counter-1", "value"),
            "value": 1,
        }, instance_id="ISubInstruction-1"),
        "simple_button_press": "press_button_b",
    }, instance_id="ButtonB-1"))
    
    Instance("???", {
        "act": Instance("ActOnEntity", {
            "entity": Instance("File-1"),
            "act": Instance("SaveAct"),
        }),
        "reaction": Instance("ActOnEntity", {
            "entity": Instance("Function-func12"),
            "act": Instance("CallAct"),
        })
    })
    
    simple_planning_strategy(goal)
    
    
if __name__ == "__main__":
    main()
