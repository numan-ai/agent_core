class BaseHierarchy:
    def get_parents(self, cid: str, include_self=True) -> list[str]:
        pass
    
    def get_children(self, cid: str, include_self=False) -> list[str]:
        pass
