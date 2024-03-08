import agci
import pytest

from src.knowledge_base.in_memory_kb import InMemoryKB
from src.knowledge_base.module import KBEdgeType
from src.unified_graph.graph import UGraph
from src.world_model.instance import Instance
from src.world_model.module import WorldModel
    
    
KB_NODES = [{
    "id": 0,
    "label": "Concept",
    "data": {"name": "Fruit"},
}, {
    "id": 1,
    "label": "Concept",
    "data": {"name": "FruitClass"},
}, {
    "id": 2,
    "label": "Concept",
    "data": {"name": "Apple"},
}, {
    "id": 3,
    "label": "Concept",
    "data": {"name": "AppleClass"},
}, {
    "id": 4,
    "label": "Field",
    "data": {"name": "name"},
}, {
    "id": 5,
    "label": "Field",
    "data": {"name": "age"},
}, {
    "id": 6,
    "label": "Field",
    "data": {"name": "owner"},
}, {
    "id": 7,
    "label": "Concept",
    "data": {"name": "Person"},
}, {
    "id": 8,
    "label": "Field",
    "data": {"name": "fruit"},
}, {
    "id": 9,
    "label": "Field",
    "data": {"name": "is_john"},
}, {
    "id": 10,
    "label": "Field",
    "data": {"name": "name"},
}, ]

KB_EDGES = [
    (0, 1, KBEdgeType.CLASS),
    (2, 3, KBEdgeType.CLASS),
    (2, 0, KBEdgeType.PARENT),
    (3, 1, KBEdgeType.PARENT),
    (2, 4, KBEdgeType.FIELD_NODE),
    (0, 5, KBEdgeType.FIELD_NODE),
    (0, 6, KBEdgeType.FIELD_NODE),
    (7, 8, KBEdgeType.FIELD_NODE),
    (7, 9, KBEdgeType.FIELD_NODE),
    (7, 10, KBEdgeType.FIELD_NODE),
    (6, 8, KBEdgeType.FIELD_REVERSE),
]

AC_CODE = """
def get_field(concept: Person, field: IsJohn):
    # set_field(concept, "PersonNameField", "John")
    return get_field(concept, "PersonNameField", "John")
    
    
def change_name_to_mike(concept: Person):
    set_field(concept, "PersonNameField", "Mike")
"""


@pytest.fixture(scope="session")
def ugi():
    kb = InMemoryKB(
        nodes=KB_NODES,
        edges=KB_EDGES
    )
    wm = WorldModel(core=None)
    wm.add(Instance("Apple", {
        "name": Instance("String", {"value": "AppleName"}),
        "age": Instance("Number", {"value": 1}),
        "owner": Instance("Person", {
            "name": Instance("String", {"value": "PersonName"}),
        }, instance_id="person-1"),
    }, instance_id="apple-1"))
    
    interpreter = agci.StepInterpreter({})
    interpreter.load_code(AC_CODE)
    
    return UGraph(
        knowledge_base=kb,
        world_model=wm,
        ac_graph=interpreter.combined_graph,
    )


def test_kb_get_concept(ugi):
    ug_fruit = ugi.get_concept("Fruit")
    assert ug_fruit is not None
    assert ug_fruit.underlying.id == 0
    
    
def test_kb_get_concept_does_not_exist(ugi):
    ug_fruit = ugi.get_concept("?????")
    assert ug_fruit is None


def test_kb_get_concept_field(ugi):
    ug_fruit = ugi.get_concept("Apple")
    assert ug_fruit is not None
    
    ug_field = ug_fruit.get_field("name")
    assert ug_field is not None
    
    assert ug_field.underlying.id == 4
    
    
def test_kb_get_concept_field_concept(ugi):
    ug_fruit = ugi.get_concept("Apple")
    assert ug_fruit is not None
    
    ug_field = ug_fruit.get_field("name")
    assert ug_field is not None
    
    ug_fruit = ug_field.get_concept()
    assert ug_fruit is not None
    
    assert ug_fruit.underlying.id == 2
    

def test_kb_get_concept_field_inherited(ugi):
    ug_fruit = ugi.get_concept("Apple")
    assert ug_fruit is not None
    
    ug_field = ug_fruit.get_field("age")
    assert ug_field is not None
    
    assert ug_field.underlying.id == 5


def test_kb_get_class(ugi):
    ug_fruit = ugi.get_concept("Apple")
    assert ug_fruit is not None
    
    ug_fruit_class = ug_fruit.get_class()
    assert ug_fruit_class is not None
    
    assert ug_fruit_class.underlying.id == 3
    
    ug_fruit = ug_fruit_class.get_instance()
    assert ug_fruit is not None
    
    assert ug_fruit.underlying.id == 2
    
    
def test_wm_instance_concept(ugi):
    ug_apple = ugi.get_wm_instance("apple-1")
    ug_apple_concept = ug_apple.get_concept()
    
    assert ug_apple_concept is not None
    assert ug_apple_concept.underlying.id == 2


def test_wm_instance_field_value(ugi):
    ug_apple = ugi.get_wm_instance("apple-1")
    ug_apple_name = ug_apple.get_field_value("name")
    
    assert ug_apple_name is not None
    assert ug_apple_name.underlying.fields.value == "AppleName"


def test_wm_instance_field_reverse(ugi):
    ug_person = ugi.get_wm_instance("person-1")
    ug_apple = ug_person.get_field_value("fruit")
    
    assert ug_apple is not None
    assert ug_apple.underlying.id == "apple-1"


def test_wm_instance_field_reverse(ugi):
    ug_concept = ugi.get_concept("Person")
    assert ug_concept is not None
    
    ug_field = ug_concept.get_field("name")
    assert ug_field is not None
    
    ug_functions = ug_field.get_setters()
    assert len(ug_functions) == 1
    assert ug_functions[0]
