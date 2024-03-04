from src.knowledge_base.concept import Concept


class BaseHierarchy:
    def get_parents(self, cid: str, include_self=True) -> list[str]:
        pass
    
    def get_children(self, cid: str, include_self=False) -> list[str]:
        pass


class PlainHierarchy:
    def get_parents(self, cid: str, include_self=True) -> list[str]:
        if not include_self:
            return []
        return [Concept.get_name(cid), ]
    
    def get_children(self, cid: str, include_self=False) -> list[str]:
        if not include_self:
            return []
        return [Concept.get_name(cid), ]
    

def is_child(hierarchy: BaseHierarchy, concept: Concept, parent: Concept) -> bool:
    if parent.name == 'Concept':
        assert parent.fields == {}
        return True
    
    if parent.name not in hierarchy.get_parents(concept.get_cid()):
        return False

    for field_name, field_value in parent.fields.items():
        concept_field_value = concept.fields.get(field_name)
        if concept_field_value is None:
            return False
        
        if not is_child(hierarchy, concept_field_value, field_value):
            return False
    
    return True