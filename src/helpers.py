import copy
from src.concept import Concept
from src import KBNode, KBEdgeType, KBEdgeDirection
from src.instance import Instance
from src.interfaces import BaseKnowledgeBase
from src.outcomes import find_connected_outcome_act


def iterate_hierarchy(kb: BaseKnowledgeBase, kb_node: KBNode) -> list[KBNode]:
    parents = kb.get_parents(kb_node.data['name'], direct=True)

    already_visited = set()
    while parents:
        next_parents = []
        
        for parent in parents:
            if parent.id in already_visited:
                continue
            already_visited.add(parent.id)
            
            yield parent
            
            next_parents.extend(kb.get_parents(parent.data['name'], direct=True))
        
        parents = next_parents
        
        
def iterate_hierarchy_down(kb: BaseKnowledgeBase, kb_node: KBNode, field_expansion=False) -> list[KBNode]:
    parents = kb.get_children(kb_node.data['name'], direct=True, field_expansion=field_expansion)

    already_visited = set()
    while parents:
        next_parents = []
        
        for parent in parents:
            if parent.id in already_visited:
                continue
            already_visited.add(parent.id)
            
            yield parent
            
            next_parents.extend(kb.get_children(parent.data['name'], direct=True, field_expansion=field_expansion))
        
        parents = next_parents
        

def specialize_concept(kb: BaseKnowledgeBase, concept: Concept) -> list[Concept]:
    fill_missing_concept_fields(kb, concept)
    if not concept.fields:
        return [concept, ]
    
    result = [concept, ]
    
    concept_node = kb.find_concept(concept.get_cid())
    
    for child in iterate_hierarchy_down(kb, concept_node, field_expansion=True):
        child_concept = Concept(child.data['name'])
        fill_missing_concept_fields(kb, child_concept)
        
        if not child_concept.fields:
            continue
        
        print(child_concept)
        
        for field_name, field_value in child_concept.fields.items():
            if not is_child_of(kb, field_value, concept.fields[field_name]):
                break
        else:
            result.append(Concept(child.data['name'], copy.deepcopy(child_concept.fields)))
            
    return result
    
def get_concept_fields(kb: BaseKnowledgeBase, concept: Concept) -> dict[str, str]:
    concept_kb_node = kb.find_concept(concept.get_cid())
    
    direct_fields = kb.out_dict(
        node_id=concept_kb_node.id,
        edge_type=KBEdgeType.FIELD,
        edge_filters=None,
        key='name',
        direction=KBEdgeDirection.OUT,
        direct=True,
    )
    
    node_fields = kb.out_dict(
        node_id=concept_kb_node.id,
        edge_type=KBEdgeType.FIELD_NODE,
        edge_filters=None,
        key='name',
        direction=KBEdgeDirection.OUT,
        direct=True,
    )
    
    fields = {**direct_fields, **node_fields}
    
    for parent in iterate_hierarchy(kb, concept_kb_node):
        direct_fields = kb.out_dict(
            node_id=parent.id,
            edge_type=KBEdgeType.FIELD,
            edge_filters=None,
            key='name',
            direction=KBEdgeDirection.OUT,
            direct=True,
        )
        
        node_fields = kb.out_dict(
            node_id=parent.id,
            edge_type=KBEdgeType.FIELD_NODE,
            edge_filters=None,
            key='name',
            direction=KBEdgeDirection.OUT,
            direct=True,
        )
        
        parent_fields = {**direct_fields, **node_fields}
        parent_fields.update(fields)
        fields = parent_fields
        
    return {
        field_name: field_node.data['name'] for field_name, field_node in fields.items()
    }


def fill_missing_concept_fields(kb: BaseKnowledgeBase, concept: Concept):
    concept_fields = get_concept_fields(kb, concept)
    for field_name, field_concept in concept_fields.items():
        if field_name not in concept.fields:
            concept.fields[field_name] = Concept(field_concept)


def is_instance_of(kb: BaseKnowledgeBase, instance_concept: Concept, class_concept: Concept) -> bool:
    for _class in iterate_concept_classes(kb, instance_concept):
        print(_class)


def iterate_concept_classes(kb: BaseKnowledgeBase, instance_concept: Concept) -> list[Concept]:
    instance_kb_node = kb.find_concept(instance_concept.get_cid())
    already_visited = set()

    for _class in kb.out(instance_kb_node.id, KBEdgeType.CLASS):
        if _class.id in already_visited:
            continue
        already_visited.add(_class.id)
        yield _class
        
    for kb_node in iterate_hierarchy(kb, instance_kb_node):
        for _class in kb.out(kb_node.id, KBEdgeType.CLASS):
            if _class.id in already_visited:
                continue
            already_visited.add(_class.id)
            yield _class
            

def iterate_specified_children(kb, concept: Concept):
    fill_missing_concept_fields(kb, concept)

    kb_node = kb.find_concept(concept.name)
    
    for child in iterate_hierarchy_down(kb, kb_node, field_expansion=True):
        print(child)

        child_concept = Concept(child.data['name'])
        fill_missing_concept_fields(kb, child_concept)
        
        for field_name, field_value in child_concept.fields.items():
            if not is_child_of(kb, concept.fields[field_name], field_value):
                break
        else:
            yield child


def is_instance_of(kb: BaseKnowledgeBase, instance_concept: Concept, class_concept: Concept) -> bool:
    child_kb_node = kb.find_concept(instance_concept.get_cid())
    
    classes = kb.out(child_kb_node.id, KBEdgeType.CLASS)
    
    for _class in classes:
        if _class.data['name'] == class_concept.name:
            return True
    
    for parent in iterate_hierarchy(kb, child_kb_node):
        classes = kb.out(parent.id, KBEdgeType.CLASS)
        
        for _class in classes:
            if _class.data['name'] == class_concept.name:
                return True
            
    return False


def is_child_of(kb: BaseKnowledgeBase, child_concept: Concept, parent_concept: Concept) -> bool:
    child_cid = child_concept.get_cid()
    parent_cid = parent_concept.get_cid()
    
    if child_cid == parent_cid:
        return True    
        
    fill_missing_concept_fields(kb, child_concept)
    fill_missing_concept_fields(kb, parent_concept)
    
    child_kb_node = kb.find_concept(child_concept.get_cid())
    
    if child_concept.name == parent_concept.name:
        # TODO: handle the case where cids are different,
        # like when field value is a child
        return child_concept.get_cid() == parent_concept.get_cid()
    
    for parent in iterate_hierarchy(kb, child_kb_node):
        if parent.data['name'] == parent_concept.name:
            return True
    
    for child in iterate_hierarchy_down(kb, child_kb_node, field_expansion=True):
        if child.data['name'] != parent_concept.name:
            continue
                
        child_concept = Concept(child.data['name'])
        fill_missing_concept_fields(kb, child_concept)
        
        for field_name, field_value in child_concept.fields.items():
            if not is_child_of(kb, field_value, parent_concept.fields[field_name]):
                break
        else:
            return True
            
    return False


def find_associated_task(kb, instance: Instance):
    """ Might change instance in case of outcome act."""
    try:
        task_node, new_instance = next(_find_associated_task(kb, instance))
        return task_node.data['name'], new_instance
    except StopIteration:
        raise Exception(f"Task for concept '{instance.concept_name}' not found")


def _find_direct_task(kb, kb_concept, initial_instance) -> KBNode:
    print('checking', kb_concept.data['name'])

    tasks = kb.out(kb_concept.id, KBEdgeType.TASK)
    for task in tasks:
        yield task, initial_instance
    
    connected_outcome_act = find_connected_outcome_act(kb, Concept(
        kb_concept.data['name'],
    ), initial_instance)
    
    if connected_outcome_act:
        print('Found connected outcome act', connected_outcome_act)
        yield from _find_associated_task(kb, connected_outcome_act)
    

def _find_associated_task(kb, instance: Instance) -> tuple[KBNode, Instance]:
    kb_concept = kb.find_concept(instance.concept_name)
    yield from _find_direct_task(kb, kb_concept, instance)
    
    for kb_child in iterate_specified_children(kb, instance.get_concept()):
        yield from _find_direct_task(kb, kb_child, instance)
        
    for kb_parent in iterate_hierarchy(kb, kb_concept):
        yield from _find_direct_task(kb, kb_parent, instance)
