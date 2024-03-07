import pytest

from src.knowledge_base.in_memory_kb import InMemoryKB
from src.knowledge_base.module import KBEdgeType
from src.unified_graph.graph import UGraph
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
}]

KB_EDGES = [
    (0, 1, KBEdgeType.CLASS),
    (2, 3, KBEdgeType.CLASS),
    (2, 0, KBEdgeType.PARENT),
    (3, 1, KBEdgeType.PARENT),
    (2, 4, KBEdgeType.FIELD_NODE),
]
    
    
@pytest.fixture(scope="session")
def ugi():
    kb = InMemoryKB(
        nodes=KB_NODES,
        edges=KB_EDGES
    )
    wm = WorldModel(core=None)
    
    return UGraph(
        knowledge_base=kb, 
        world_model=wm,
    )


def test_get_concept_exists(ugi):
    ug_fruit = ugi.get_concept("Fruit")
    assert ug_fruit is not None
    assert ug_fruit.underlying.id == 0
    
    
def test_get_concept_does_not_exist(ugi):
    ug_fruit = ugi.get_concept("?????")
    assert ug_fruit is None


def test_get_concept_field_exists(ugi):
    ug_fruit = ugi.get_concept("Apple")
    assert ug_fruit is not None
    
    ug_field = ug_fruit.get_field("name")
    assert ug_field is not None
    
    assert ug_field.underlying.id == 4
    
    
def test_get_concept_field_concept_exists(ugi):
    ug_fruit = ugi.get_concept("Apple")
    assert ug_fruit is not None
    
    ug_field = ug_fruit.get_field("name")
    assert ug_field is not None
    
    assert ug_field.underlying.id == 4
