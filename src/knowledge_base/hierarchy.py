from collections import defaultdict

from src.knowledge_base.concept import Concept


class BaseHierarchy:
    def get_parents(self, cid: str, include_self=True) -> list[str]:
        pass
    
    def get_children(self, cid: str, include_self=False) -> list[str]:
        pass
    
    def is_subconcept(self, cid: str, parent_cid: str) -> bool:
        return parent_cid in self.get_parents(cid)


class PlainHierarchy(BaseHierarchy):
    def get_parents(self, cid: str, include_self=True) -> list[str]:
        if not include_self:
            return []
        return [Concept.get_name(cid), ]
    
    def get_children(self, cid: str, include_self=False) -> list[str]:
        if not include_self:
            return []
        return [Concept.get_name(cid), ]
    
    
class DictHierarchy(BaseHierarchy):
    def __init__(self, *, 
                 children: dict[str, list[str]] = None,
                 parents: dict[str, list[str]] = None):
        if children is not None:
            self.children = children
            self.parents = self._invert_dict(children)
        elif parents is not None:
            self.parents = parents
            self.children = self._invert_dict(parents)
        elif children is not None and parents is not None:
            raise ValueError("Provide only children or parents")
        else:
            raise ValueError("Provide children or parents")

    def get_parents(self, cid: str, include_self=True) -> list[str]:
        self_as_parent = [cid, ] if include_self else []
        
        try:
            result = set(self_as_parent)

            for parent in self.parents[cid]:
                result.add(parent)
                result.update(self.get_parents(parent))

            return sorted(list(result))
        except KeyError:
            return self_as_parent

    def get_children(self, cid: str, include_self=False) -> list[str]:
        self_as_parent = [cid, ] if include_self else []
        
        try:
            return self.children[cid] + self_as_parent
        except KeyError:
            return self_as_parent

    @staticmethod
    def _invert_dict(parents):
        children = defaultdict(list)
        for child, pars in parents.items():
            for parent in pars:
                children[parent].append(child)

        return children
    

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
