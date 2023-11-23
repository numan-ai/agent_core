import weakref

from src.concept import Concept
from src.helpers import is_child_of, is_instance_of
from src.instance import Instance
from src.knowledge_base import KnowledgeBase


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

    def _check_object_matches(self, kb, obj: Instance, sub_obj: Instance, description=None): 
        obj_con = obj.get_concept()
        sub_obj_con = sub_obj.get_concept()
        
        if is_instance_of(kb, sub_obj_con, obj_con):
            return sub_obj

        # separate description and the object if the description is present
        if obj.concept_name == 'ObjectWithDescription':
            # TODO: support multiple descriptions
            description = obj.fields['description']
            obj = obj.fields['object']

        for key, sub_value in sub_obj.fields.items():
            if description is not None:
                associations = self._get_description_word_associations(kb, key)
                
                if description.concept_name in associations:
                    # description was resolved, setting it to None
                    description = None

            if not isinstance(sub_value, Instance):
                # a list of Entities, or a literal
                continue

            result = self._check_object_matches(kb, obj, sub_value, description)
            if result is not None and description is None:
                return result

        return None

    def search(self, kb, obj: Instance):
        if obj.concept_name == "DefiniteEntityReference":
            obj = obj.fields['concept']
            
        for sub_obj in reversed(self.objects):
            result = self._check_object_matches(kb, obj, sub_obj)
            if result is not None:
                return result
        return None


class ReferenceManager:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
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
            if isinstance(field, Instance) and field.concept_name == 'String':
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
        for ctx in reversed(self.contexts):
            new_obj = ctx.search(self.kb, obj)
            if new_obj is not None:
                break
        else:
            if required:
                # object wasn't found, returning the original object
                breakpoint()
                pass
            new_obj = obj
            
        return new_obj
