import abc
from dataclasses import dataclass
import enum
from typing import Self

from dotenv import load_dotenv

from src.agent_core import AgentCore
from src.knowledge_base.module import (
    KnowledgeBase,
    KBNode,
    KBEdgeType,
)
from src.knowledge_base.reverse_specialisation import reverse_specialise
from src.world_model.instance import Instance
from src.world_model.module import WorldModel


load_dotenv()

kb = KnowledgeBase(None)


class LRDNode(abc.ABC):
    pass


@dataclass
class Concept(LRDNode):
    name: str
    node_id: str

    @classmethod
    def from_name(cls, name: str):
        concept_node = kb.find_concept(name)
        return cls(name, concept_node.id)
    
    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.data['name'], node.id)

    def get_fields(self):
        field_nodes = kb.out_dict2(self.node_id, KBEdgeType.FIELD_NODE)
        
        return {
            key: ConceptField.from_node(field_nodes)
            for key, field_nodes in field_nodes.items()
        }
    
    def get_field(self, name: str) -> 'ConceptField':
        field_nodes = kb.out_dict2(self.node_id, KBEdgeType.FIELD_NODE)
        return ConceptField.from_node(field_nodes[name])


@dataclass
class ConceptField(LRDNode):
    node_id: str
    name: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id, node.data['name'])

    def get_concept(self) -> Concept:
        concept_nodes = kb.in_(self.node_id, KBEdgeType.FIELD_NODE)
        assert len(concept_nodes) == 1
        return Concept.from_node(concept_nodes[0])
    
    def get_getters(self) -> list['ConceptFieldGetter']:
        getter_nodes = kb.out(self.node_id, KBEdgeType.FIELD_GETTER)
        return [
            ConceptFieldGetter.from_node(getter_node)
            for getter_node in getter_nodes
        ]
    
    def get_setters(self) -> list['ConceptFieldSetter']:
        setter_nodes = kb.in_(self.node_id, KBEdgeType.FIELD_SETTER_TARGET)
        return [
            ConceptFieldSetter.from_node(setter_node)
            for setter_node in setter_nodes
        ]
    
    def get_setter_actions(self) -> list['OnActionLRDNode']:
        """ Returns actions that update this field
        This is a temporary(?) solution for easier traversal
        """
        setter_nodes = kb.out(self.node_id, KBEdgeType.FIELD_SETTER_ACTION)
        return [
            OnActionLRDNode.from_node(setter_node)
            for setter_node in setter_nodes
        ]
    
    def get_setter_events(self) -> list['OnEventLRDNode']:
        """ Returns events that update this field
        This is a temporary(?) solution for easier traversal
        """
        setter_nodes = kb.out(self.node_id, KBEdgeType.FIELD_SETTER_EVENT)
        return [
            OnEventLRDNode.from_node(setter_node)
            for setter_node in setter_nodes
        ]


@dataclass
class LRDLogicNode(LRDNode):
    node_id: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id)


@dataclass
class BinaryLRDLogicNode(LRDLogicNode):    
    def get_left(self):
        left = kb.out(self.node_id, KBEdgeType.CONDITION_LEFT)
        assert len(left) == 1
        return get_logic_value_node(left[0])
    
    def get_right(self):
        left = kb.out(self.node_id, KBEdgeType.CONDITION_RIGHT)
        assert len(left) == 1
        return get_logic_value_node(left[0])
    


@dataclass
class ConditionLRDNode(BinaryLRDLogicNode):
    pass


@dataclass
class ChangeFieldLRDNode(LRDLogicNode):
    node_id: str
    change_type: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id, node.data['name'])
    
    def get_value(self):
        value = kb.out_one(self.node_id, KBEdgeType.FIELD_CHANGE_VALUE)
        return get_logic_value_node(value)


@dataclass
class BinaryBooleanLRDNode(BinaryLRDLogicNode):
    pass


@dataclass
class BinaryMathLRDNode(BinaryLRDLogicNode):
    pass


@dataclass
class LRDConstant(LRDNode):
    node_id: str
    value: any

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id, node.data['name'])


def get_logic_value_node(node: KBNode):
    if node.label == 'ObjectField':
        return ConceptInstanceField.from_node(node)
    elif node.label == 'Constant':
        return LRDConstant.from_node(node)
    else:
        raise NotImplementedError(f"Unknown logic value node type: {node.label}")
    

def get_logic_node(node: KBNode):
    if node.label == 'Condition':
        return ConditionLRDNode.from_node(node)
    elif node.label == 'ChangeField':
        return ChangeFieldLRDNode.from_node(node)
    elif node.label == 'TriggerEvent':
        return TriggerEventLRDNode.from_node(node)
    else:
        raise NotImplementedError(f"Unknown logic node type: {node.label}")


@dataclass
class ConceptFieldGetter(LRDNode):
    node_id: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id)
    
    def get_instance(self) -> 'ConceptInstance':
        instance_nodes = kb.out(self.node_id, KBEdgeType.GETTER_INSTANCE)
        assert len(instance_nodes) == 1
        return ConceptInstance.from_node(instance_nodes[0])

    def get_logic(self):
        logic_nodes = kb.out(self.node_id, KBEdgeType.GETTER_LOGIC)
        assert len(logic_nodes) == 1
        return get_logic_node(logic_nodes[0])
    

@dataclass
class ConceptFieldSetter(LRDNode):
    node_id: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id)
    

@dataclass
class OnActionLRDNode(LRDNode):
    node_id: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id)
    
    def get_concept(self) -> Concept:
        concept_node = kb.out_one(self.node_id, KBEdgeType.ON_ACTION_CONCEPT)
        return Concept.from_node(concept_node)
    
    def get_logic(self):
        logic_node = kb.out_one(self.node_id, KBEdgeType.ON_ACTION_LOGIC)
        return get_logic_node(logic_node)
    
    def get_object(self) -> 'ConceptInstance':
        instance_node = kb.out_one(self.node_id, KBEdgeType.ON_ACTION_OBJECT)
        return ConceptInstance.from_node(instance_node)
    

@dataclass
class OnEventLRDNode(LRDNode):
    node_id: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id)
    
    def get_concept(self) -> Concept:
        concept_node = kb.out_one(self.node_id, KBEdgeType.ON_EVENT_CONCEPT)
        return Concept.from_node(concept_node)
    
    def get_logic(self):
        logic_node = kb.out_one(self.node_id, KBEdgeType.ON_EVENT_LOGIC)
        return get_logic_node(logic_node)
    
    def get_object(self) -> 'ConceptInstance':
        instance_node = kb.out_one(self.node_id, KBEdgeType.ON_EVENT_OBJECT)
        return ConceptInstance.from_node(instance_node)


@dataclass
class ConceptInstance:
    node_id: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id)
    
    def get_fields(self):
        field_nodes = kb.out(self.node_id, KBEdgeType.INSTANCE_FIELD)
        
        return [
            ConceptInstanceField.from_node(field_node)
            for field_node in field_nodes
        ]


@dataclass
class ConceptInstanceField:
    node_id: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id)
    
    def get_concept_field(self) -> ConceptField:
        field_nodes = kb.out(self.node_id, KBEdgeType.FIELD_CONCEPT_FIELD)
        assert len(field_nodes) == 1
        return ConceptField.from_node(field_nodes[0])
    
    def get_sub_fields(self) -> list[Self]:
        field_nodes = kb.out(self.node_id, KBEdgeType.INSTANCE_FIELD)
        return [
            ConceptInstanceField.from_node(field_node)
            for field_node in field_nodes
        ]


@dataclass
class TriggerEventLRDNode(LRDLogicNode):
    def get_object(self) -> ConceptInstance | ConceptInstanceField:
        instance_node = kb.out_one(self.node_id, KBEdgeType.TRIGGER_EVENT_OBJECT)
        if instance_node.label == 'ObjectField':
            return ConceptInstanceField.from_node(instance_node)
        else:
            return ConceptInstance.from_node(instance_node)
        
    def get_concept(self) -> Concept:
        concept_node = kb.out_one(self.node_id, KBEdgeType.TRIGGER_EVENT_CONCEPT)
        return Concept.from_node(concept_node)


def build_lrd_obj_map(lrd_node: LRDNode, instance: Instance, result = None):
    if result is None:
        result = {}

    if isinstance(lrd_node, ConceptInstance):
        result[lrd_node.node_id] = instance
        fields = lrd_node.get_fields()

        for field in fields:
            concept_field = field.get_concept_field()
            instance_field = Instance("InstanceField", {
                "instance": instance,
                "field": concept_field.name,
            })

            result[field.node_id] = instance_field
            build_lrd_obj_map(
                field,
                instance_field,
                result,
            )
    elif isinstance(lrd_node, ConceptInstanceField):
        sub_fields = lrd_node.get_sub_fields()
        for field in sub_fields:
            concept_field = field.get_concept_field()
            instance_field = Instance("InstanceField", {
                "instance": instance,
                "field": concept_field.name,
            })
            result[field.node_id] = instance_field
            build_lrd_obj_map(
                field,
                instance_field,
                result,
            )
    else:
        raise NotImplementedError(f"Unknown LRD node type: {lrd_node}")

    return result


def construct_goal_from_getter(getter, instance, expected_value):
    if expected_value.concept_name in {"Boolean", "Number", "String"}:
        expected_value = expected_value.fields.value
    
    obj = getter.get_instance()

    lrd_obj_map = build_lrd_obj_map(obj, instance)

    logic = getter.get_logic()

    if isinstance(logic, ConditionLRDNode):
        left = logic.get_left()
        right: LRDConstant = logic.get_right()

        new_instance = lrd_obj_map[left.node_id]
        new_value = Instance("Number", {
            "value": right.value,
        })

        if expected_value is True:
            return Instance("GoalFieldEqual", {
                "instance": new_instance,
                "value": new_value,
            })
        elif expected_value is False:
            return Instance("GoalFieldNotEqual", {
                "instance": new_instance,
                "value": new_value,
            })
        else:
            raise ValueError(
                "Expected value must be a boolean for"
                f"a conditional logic, got {expected_value}")
    else:
        raise NotImplementedError()


class GoalDirection(enum.Enum):
    INCREASE = enum.auto()
    DECREASE = enum.auto()
    ANY_CHANGE = enum.auto()


def find_next_goal(kb, goal: Instance) -> Instance:
    if goal.concept_name in {"GoalFieldEqual", "GoalFieldNotEqual"}:
        return find_options_for_equality_goal(kb, goal)
    elif goal.concept_name in {"GoalTriggerEvent", }:
        return find_options_for_event_goal(kb, goal)
    
    raise NotImplementedError()


def _is_logic_relevant_to_goal(logic, goal) -> bool:
    assert isinstance(logic, ChangeFieldLRDNode)
    assert isinstance(goal, Instance)
    assert goal.concept_name in {"GoalFieldEqual", "GoalFieldNotEqual"}

    logic_value = logic.get_value()
    assert isinstance(logic_value, LRDConstant)
    logic_value = logic_value.value

    goal_value = goal.fields.value.fields.value
    if goal.concept_name == "GoalFieldEqual":
        desired_direction = (
            GoalDirection.INCREASE if goal_value > logic_value else GoalDirection.DECREASE
        )
    elif goal.concept_name == "GoalFieldNotEqual":
        desired_direction = GoalDirection.ANY_CHANGE

    if logic.change_type == "=":
        goal_direction = (
            GoalDirection.INCREASE if goal_value > logic_value else GoalDirection.DECREASE
        )
    elif logic.change_type == "+=":
        goal_direction = (
            GoalDirection.INCREASE if goal_value >= 0 else GoalDirection.DECREASE
        )
    elif logic.change_type == "-=":
        goal_direction = (
            GoalDirection.INCREASE if goal_value <= 0 else GoalDirection.DECREASE
        )

    if desired_direction == GoalDirection.ANY_CHANGE:
        # TODO: check that the change is needed (1) and will be done (2)
        return True
    
    return goal_direction == desired_direction


def find_options_for_event_goal(kb, goal) -> Instance:
    reverse_specialise(goal.fields.instance, kb)

    out_fields = goal.fields.instance.out_fields.get()

    for out_instance, out_field in out_fields:
        con = Concept.from_name(out_instance.concept_name)

        try:
            field = con.get_field(out_field.name)
        except KeyError:
            continue

        # find events that trigger this event
        events = field.get_setter_events()

        for event in events:
            if event.get_concept().name != goal.fields.event:
                continue

            evt_obj = event.get_object()
            evt_logic = event.get_logic()
            lrd_obj_map = build_lrd_obj_map(evt_obj, out_instance)
            
            return Instance("GoalTriggerEvent", {
                "event": evt_logic.get_concept().name,
                "instance": lrd_obj_map[evt_obj.node_id],
            })
        
        # find actions that trigger this event
        actions = field.get_setter_actions()

        for action in actions:
            act_obj = action.get_object()
            lrd_obj_map = build_lrd_obj_map(act_obj, out_instance)

            return Instance("GoalInvokeAction", {
                "action": action.get_concept().name,
                "instance": lrd_obj_map[act_obj.node_id],
            })
        
    raise NotImplementedError()


def find_options_for_equality_goal(kb: KnowledgeBase, goal: Instance) -> Instance:
    """ Will look for getters, actions or events that set the desired field
    if the goal wants to set the field of the field, then 
    we will take the last field in the chain.
    """

    instance_field = goal.fields.instance
    target_instance = instance_field.fields.instance
    target_field_name = instance_field.fields.field

    while target_instance.concept_name == "InstanceField":
        target_instance = target_instance.fields.instance.fields[target_instance.fields.field]

    reverse_specialise(target_instance, kb)

    con = Concept.from_name(target_instance.concept_name)
    field = con.get_field(goal.fields.instance.fields.field)

    # find events that set this field
    events = field.get_setter_events()

    for event in events:
        logic = event.get_logic()

        if isinstance(logic, TriggerEventLRDNode):
            breakpoint()

        if not _is_logic_relevant_to_goal(logic, goal):
            continue

        # TODO: fix event arguments lookup
        # evt_obj = event.get_object()

        # result = build_lrd_obj_map(evt_obj, None)
        # breakpoint()
        
        return Instance("GoalTriggerEvent", {
            "event": event.get_concept().name,
            "instance": target_instance,
        })

    # find actions that set this field
    actions = field.get_setter_actions()

    for action in actions:
        logic = action.get_logic()
        if not _is_logic_relevant_to_goal(logic, goal):
            continue

        # TODO: find invokation arguments
        return Instance("GoalInvokeAction", {
            "action": action.get_concept().name,
        })

    # find getters
    getters = field.get_getters()

    for getter in getters:
        new_goal = construct_goal_from_getter(getter, target_instance, goal.fields.value)
        
        if new_goal is None:
            continue

        return new_goal

    raise NotImplementedError()


def traverse_lrd(goal: Instance) -> Instance:
    print(goal)

    while True:
        goal = find_next_goal(kb, goal)
        print(goal)
        if goal.concept_name == "GoalInvokeAction":
            break

    return goal


def main():
    btn = Instance('Button', {
        "output_pin": Instance("Pin", {"value": False}),
    })
    led = Instance('LED', {
        "is_on": Instance("Boolean", {"value": False}),
        "input_pin": Instance("Pin", {"value": False}),
        "value": Instance("Number", {"value": 0}),
    })
    wire = Instance("Wire", {
        "input_pin": btn.fields['output_pin'],
        "output_pin": led.fields['input_pin'],
    })

    btn.fields['output_pin'].fields['wire'] = wire
    led.fields['input_pin'].fields['wire'] = wire

    goal = Instance("GoalFieldEqual", {
        "instance": Instance("InstanceField", {
            "instance": led,
            "field": "is_on",
        }),
        "value": Instance("Boolean", {
            "value": True,
        }),
    })

    core = AgentCore()
    wm = core.world_model

    wm.add(led)
    wm.add(btn)
    wm.add(wire)
    wm.add(goal)

    ## TODO: do this automatically somewhere
    ## this needs to be done dynamically since the fields can be 
    ## updated on the fly, meaning that reverse specialisation 
    ## might change over time
    # reverse_specialise(wire.fields['output_pin'], kb)
    # reverse_specialise(wire.fields['input_pin'], kb)

    goal = traverse_lrd(goal)

    core.input_processor.send_event(Instance("ActOnEntity", {
        "act": Instance(goal.fields.action),
        "entity": goal.fields.instance,
    }))
    core.run()



if __name__ == '__main__':
    main()
