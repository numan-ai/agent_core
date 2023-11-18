import pytest
from src import helpers

from src.concept import Concept


@pytest.mark.parametrize(
    "child_cid, parent_cid, expected",
    [
        ("ActOnEntity", "ActOnEntity", True),
        ("ActOnEntity", "Act", True),
        ("ActOnEntity", "Concept", True),
        ("Concept", "ConceptClass", False),
        ("ActOnEntity", "ConceptClass", False),
        ("File", "PythonFile", False),
        ("ActOnEntity{act=RemoveAct,entity=File}", "ActRemoveFile", True),
        # ("Car{color=Red}", "RedCar", True),
        # ("EntityWithDescription{entity=Car,description=Red}", "RedCar", True),
        # ("Number__7", "Number", True),  # We don't support unique instance concepts yet
        # ("Number__7", "OddNumber", True),  # We don't support unique instance concepts yet
        # ("Car{owner=PersonYou}", "YourCar", True),  # Concepts don't exist
        ("", "", True),
    ],
)
def test_is_child_of(kb, child_cid, parent_cid, expected):
    child_concept = Concept.from_cid(child_cid)
    parent_concept = Concept.from_cid(parent_cid)
    
    assert helpers.is_child_of(kb, child_concept, parent_concept) == expected
