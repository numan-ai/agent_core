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


class StaticKBHierarchy(BaseHierarchy):
    def __init__(self, kb):
        self.kb = kb
        self.cached_children = {}
        self.cached_parents = {}
        self.prefeteched = False

    def prefetch(self):
        self.prefeteched = True
        self.cached_parents, self.cached_children = self.kb.build_hierarchy()

    def get_children(self, concept: str, include_self=False):
        if concept not in self.cached_children:
            if self.prefeteched:
                return [concept, ]
        #     node = self.kb.find_concept(concept)
        #     self.cached_children[concept] = [
        #         node.data['name']
        #         for node in self.kb.find_children(node.id)
        #     ]
        return self.cached_children[concept] + [concept]

    def get_parents(self, concept: str, include_self=True):
        # if '{' in concept:
        #     concept_obj = Concept.from_cid(concept)
        #     concept_kb = self.kb.find_concept(concept_obj.name)
        #     parents = self.kb.find_parents(concept_kb.id)
        #     augments = {}
        #     for parent in parents:
        #         augments.update(self.kb.out_dict_pair(parent.id, 'field'))
        #     augments.update(self.kb.out_dict_pair(concept_kb.id, 'field'))

        #     aug_parents = []

        #     for key, (augment_edge, augment_concept) in augments.items():
        #         if augment_edge['parent'] != '1':
        #             continue
        #         try:
        #             aug_parents.append(concept_obj.aug[key].name)
        #         except KeyError:
        #             breakpoint()
        #         aug_parents.extend(self.get_parents(concept_obj.fields[key].to_cid()))

        #     parent_names = [
        #         x.data['name'] for x in parents
        #     ]

        #     return sorted(list(set(parent_names + aug_parents + [concept_obj.name])))
    
        if concept not in self.cached_parents:
            if self.prefeteched:
                return [concept, ]
        #     try:
        #         node = self.kb.find_concept(concept)
        #     except KeyError:
        #         self.cached_parents[concept] = [concept, ]
        #         return [concept, ]
        #     self.cached_parents[concept] = [
        #         node.data['name']
        #         for node in self.kb.find_parents(node.id)
        #     ]
        return self.cached_parents[concept] + [concept]
