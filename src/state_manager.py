import weakref
from shpat.concepts import Concept, is_sub_concept
from shpat.hierarchy import StaticKBHierarchy
from shpat.knowledge_base import KnowledgeBase

from src.instance import Instance


class StageManagerContext:
    def __init__(self):
        self.objects = []
        self.text_to_object = weakref.WeakValueDictionary()

    def _get_description_word_associations(self, kb: KnowledgeBase, word) -> list[str]:
        word_node = kb.find_word(word)
        if word_node is None:
            return []

        associations = kb.find_direct_associations(word_node.id)
        return [
            association.data['name']
            for association in associations
        ]

    def _check_object_matches(self, kb, hierarchy, obj, sub_obj, description=None):        
        obj_con = obj.get_concept_obj()
        sub_obj_con = sub_obj.get_concept_obj()
            
        if is_sub_concept(hierarchy, sub_obj_con, obj_con):
            return sub_obj

        # separate description and the object if the description is present
        if obj.concept == 'ObjectWithDescription':
            # TODO: support multiple descriptions
            description = obj.fields['description']
            obj = obj.fields['object']

        for key, sub_value in sub_obj.fields.items():
            associations = self._get_description_word_associations(kb, key)
            if description is not None and description.concept in associations:
                # description was resolved, setting it to None
                description = None

            if not isinstance(sub_value, Instance):
                # a list of Entities, or a literal
                continue

            result = self._check_object_matches(kb, hierarchy, obj, sub_value, description)
            if result is not None and description is None:
                return result

        return None

    def search(self, kb, hierarchy, obj):
        for sub_obj in reversed(self.objects):
            result = self._check_object_matches(kb, hierarchy, obj, sub_obj)
            if result is not None:
                return result
        return None


class StageManager:
    def __init__(self, kb: KnowledgeBase, hierarchy: StaticKBHierarchy):
        self.kb = kb
        self.hierarchy = hierarchy
        self.contexts: list[StageManagerContext] = [
            StageManagerContext()
        ]

    def push_context(self):
        self.contexts.append(StageManagerContext())

    def pop_context(self):
        self.contexts.pop()

    @property
    def objects(self):
        return self.contexts[-1].objects

    def save(self, obj: Instance):
        self._save_obj_to_ctx(obj, self.contexts[-1])
        
    def save_global(self, obj: Instance):
        self._save_obj_to_ctx(obj, self.contexts[0])
        
    def _save_obj_to_ctx(self, obj: Instance, ctx: StageManagerContext):
        for field in obj.fields.values():
            if isinstance(field, Instance) and field.concept == 'String':
                ctx.text_to_object[field.fields['value']] = obj
                
        ctx.objects.append(obj)
        
    def find_text(self, text):
        for ctx in reversed(self.contexts):
            if text in ctx.text_to_object:
                return ctx.text_to_object[text]
            
    def find_match(self, match, required=True):
        # TODO: remove this when syntactic extractor is moved to the agent from shpat
        instance = Instance.from_dict({
            'concept': match.concept,
            'data': match.structure,
        })
        return self.find(instance, required=required)

    def find(self, obj: Instance, required=True):
        if Concept.from_uid(obj.concept).name == 'DefiniteEntityReference':
            obj = obj.fields['concept']
            concept_node = self.kb.find_concept(obj.concept)
            instance = self.kb.in_(concept_node.id, 'class')[0]
            obj = Instance(instance.data['name'])

        for ctx in reversed(self.contexts):
            new_obj = ctx.search(self.kb, self.hierarchy, obj)
            if new_obj is not None:
                # new_obj.pprint()
                # print()
                break
        else:
            if required:
                # object wasn't found, returning the original object
                breakpoint()
                pass
            new_obj = obj
            
        return new_obj
