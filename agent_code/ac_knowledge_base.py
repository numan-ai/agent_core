def create_kb_node(node_label: String):
    node = kb.new_node(node_label, {
        '_meta': '{"x": 0, "y": 0}',
    })
    return node.id


def set_kb_node_field(node_id: Number, field_name: String, field_value: Constant):
    kb.update_node_data(node_id, {
        field_name: field_value
    })


def create_kb_edge(edge_label: String, start_node_id: Number, end_node_id: Number):
    edge = kb.new_edge(edge_label, start_node_id, end_node_id, {})
    return edge.id


def upsert_kb_edge(edge_label: String, start_node_id: Number, end_node_id: Number):
    edge = kb.upsert_edge(edge_label, start_node_id, end_node_id, {})
    return edge.id


def remove_kb_node():
    pass


def remove_kb_edge():
    pass


def get_kb_node():
    pass


def get_kb_edge():
    pass


def find_concept(concept_id: String):
    return kb.find_concept(concept_id, should_raise=False)


def create_kb_concept(concept_id: String):
    node_id = create_kb_node("Concept")
    set_kb_node_field(node_id, 'name', concept_id)
    return node_id


def upsert_kb_concept(concept_id: String):
    concept = find_concept(concept_id)
    if concept:
        return concept.id
    
    return create_kb_concept(concept_id)