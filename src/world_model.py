from src.interfaces import (
    BaseHierarchy, 
    BaseKnowledgeBase,
)


class WorldModel:
    def __init__(self, kb: BaseKnowledgeBase, hierarchy: BaseHierarchy):
        self.kb = kb
        self.hierarchy = hierarchy

