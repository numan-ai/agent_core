"""
What's reverse specialisation - it's not about undoing the specialisation, it's about specialising fields:
    `Human{left_hand=Hand(), right_hand=Hand()}` first hand can be specialised to a concept of `LeftHand`
    and a second one to `RightHand`. 
Right now we don't have a way to use information about a parent of the field (and the name of a field) 
    in order to get more information about the field's concept, but it can be very useful. 
For example it is needed in LRD:
The logic of wire's output pin is different from the logic of led's input pin, 
    but both pins can have a concept of Pin, so how do we understand that they have different logic?
Both `Wire{out_pin=Pin}` and `Led{input_pin=Pin}` have the same concept of Pin inside, 
    but different logic that we want to associate with them.
We can't rely on objects always having correctly specialised concepts, so we need a way 
    to say that `Wire{out_pin=Pin}` is equivalent to `Wire{out_pin=WireOutputPin}`, 
    which will allow us to use different logic for it. 
And reverse specialisation is exactly the tool for this.
"""


from src.knowledge_base.module import KBEdgeType, KBNotFoundError, KnowledgeBase
from src.world_model.instance import Instance
from src.world_model.module import WorldModel


def reverse_specialise(instance: Instance, kb: KnowledgeBase):
    """ Reverse specialisation of fields of an instance
    Instance must be in a world model
    """
    assert instance.world_model is not None

    out_fields = instance.out_fields.get()

    specialisations = []

    for out_instance, out_field in out_fields:
        try:
            concept = kb.find_concept(out_instance.concept_name)
        except KBNotFoundError:
            continue
        field = kb.out_one(
            concept.id, KBEdgeType.FIELD_NODE,
            node_filters=(("name", out_field.name),)
        )
        field_concept = kb.out_one(field.id, KBEdgeType.FIELD_CONCEPT)

        if field_concept.data['name'] == instance.concept_name:
            continue
    
        # just checking in case the instance is more specific than the field's concept
        if kb.hierarchy.is_subconcept(field_concept.data['name'], instance.concept_name):
            specialisations.append(field_concept.data['name'])

    if len(specialisations) == 0:
        return
    
    if len(specialisations) > 1:
        # Potentially concepts can be allowed to have multiple concepts
        raise NotImplementedError('Multiple specialisations are not supported yet')
        
    instance.concept_name = specialisations[0]


def main():
    core = None
    kb = KnowledgeBase(core)
    world = WorldModel(core)
    instance = Instance('Human', {
        'left_hand': Instance('Hand', {}),
        'right_hand': Instance('Hand', {}),
    })
    world.add(instance)

    reverse_specialise(instance.fields.left_hand, kb)

    assert instance.fields.left_hand.concept_name == 'LeftHand'


if __name__ == '__main__':
    main()
