from src.instance import Instance
from src.interfaces.base_knowledge_base import KBEdgeType


def create_instance_with_fields(kb, concept_name):
    concept_node = kb.find_concept(concept_name)
    field_nodes = kb.out_dict(concept_node.id, KBEdgeType.FIELD)
    
    fields = {}
    
    for field_name, field_node in field_nodes.items():
        fields[field_name] = create_instance_with_fields(kb, field_node.data['name'])
    
    return Instance(concept_name, fields)


def _take_field_value(instance, field_path):
    """ Field path looks like this: field1.inner_field2.inner_field3"""
    field_names = field_path.split('.')
    for field_name in field_names:
        instance = instance.fields[field_name]
    return instance


def _set_field_value(instance, field_path, value):
    """ Field path looks like this: field1.inner_field2.inner_field3"""
    field_names = field_path.split('.')
    for field_name in field_names[:-1]:
        instance = instance.fields[field_name]
    instance.fields[field_names[-1]] = value


def find_connected_outcome_act(kb, concept, initial_instance):
    """ Find connected outcome act for given concept and initial act.
    concept: used to find the connected outcome act.
    initial_instance: used to get the initial fields when filling the new act.
    """
    concept_node = kb.find_concept(concept.name)
    outcomes = kb.get_outcomes(concept_node.id)
    if not outcomes:
        return
    
    if len(outcomes) > 1:
        raise NotImplementedError()
    
    act_node, outcome_node = outcomes[0]
    
    act_instance = create_instance_with_fields(kb, act_node.data['name'])
    
    field_values = kb.out_dict(outcome_node.id, KBEdgeType.FIELD)
    
    for field_path, outcome_field_node in field_values.items():
        field_value = _take_field_value(initial_instance, outcome_field_node.data['name'])
        _set_field_value(act_instance, field_path, field_value)
    
    return act_instance