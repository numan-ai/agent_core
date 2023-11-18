import pytest

from src.knowledge_base import KnowledgeBase


@pytest.fixture(scope="session")
def kb():
    return KnowledgeBase()
