import abc
from dataclasses import dataclass
from typing import Self

from dotenv import load_dotenv

from src.knowledge_base.module import (
    KnowledgeBase,
    KBNode,
    KBEdgeType,
)
from src.world_model.instance import Instance


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
    def from_node(cls, node: KBNode):
        return cls(node.id, node.data['name'])

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
    
    def get_getter(self) -> 'ConceptFieldGetter':
        getter_nodes = kb.out(self.node_id, KBEdgeType.FIELD_GETTER)
        assert len(getter_nodes) == 1
        return ConceptFieldGetter.from_node(getter_nodes[0])
    
    def get_setters(self) -> list['ConceptFieldSetter']:
        setter_nodes = kb.in_(self.node_id, KBEdgeType.FIELD_SETTER_TARGET)
        return [
            ConceptFieldGetter.from_node(setter_node)
            for setter_node in setter_nodes
        ]


@dataclass
class LRDLogicNode(LRDNode):
    pass


@dataclass
class ConceptFieldSetter(LRDLogicNode):
    node_id: str


@dataclass
class ConditionLRDNode(LRDLogicNode):
    node_id: str

    @classmethod
    def from_node(cls, node: KBNode) -> Self:
        return cls(node.id)
    
    def get_left(self):
        left = kb.out(self.node_id, KBEdgeType.CONDITION_LEFT)
        assert len(left) == 1
        return get_logic_value_node(left[0])
    
    def get_right(self):
        left = kb.out(self.node_id, KBEdgeType.CONDITION_RIGHT)
        assert len(left) == 1
        return get_logic_value_node(left[0])
    

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


@dataclass
class Goal:
    instance: Instance
    field: str
    value: any


@dataclass
class GoalEqual:
    left: Instance
    right: Instance


def build_lrd_node_map(concept_instance: ConceptInstance, instance: Instance, result = None):
    if result is None:
        result = {}
    result[concept_instance.node_id] = instance

    fields = concept_instance.get_fields()

    for field in fields:
        concept_field = field.get_concept_field()
        result[field.node_id] = instance.fields[concept_field.name]

        # TODO: add recursion for nested fields

    return result


def main():
    btn = Concept.from_name('Button')

    btn = Instance('Button', {
        "output_pin": Instance("Pin", {"value": False}),
    })
    led = Instance('LED', {
        "is_on": False,
        "input_pin": Instance("Pin", {"value": False}),
        "value": Instance("Number", {"value": 0}),
    })
    wire = Instance("Wire", {
        "input_pin": btn.fields['output_pin'],
        "output_pin": led.fields['input_pin'],
    })

    goal = Goal(
        instance=led,
        field="is_on",
        value=True,
    )

    con = Concept.from_name(goal.instance.concept_name)
    field = con.get_field(goal.field)

    getter = field.get_getter()
    instance = getter.get_instance()

    result = build_lrd_node_map(instance, led)

    logic = getter.get_logic()
    left = logic.get_left()
    right = logic.get_right()

    new_goal = GoalEqual(
        left=1,
    )

    breakpoint()
    pass


if __name__ == '__main__':
    main()
