from grass import AssociativeEnergyGraph
from src.knowledge_base.concept import Concept
from src.knowledge_base.hierarchy import (
    StaticKBHierarchy,
)
from src.knowledge_base.module import (
    KBEdgeDirection,
    KBEdgeType,
    KBNodeType, 
    KnowledgeBase,
)


class KBContext(AssociativeEnergyGraph):
    def __init__(self, kb: KnowledgeBase):
        super().__init__([])
        self.hierarchy = kb.hierarchy
        
        tasks = kb.find_nodes(KBNodeType.TASK, ())
        event_reactions_list = [
            kb.out(task.id, KBEdgeType.TASK, direction=KBEdgeDirection.IN)
            for task in tasks
        ]
        for event_reactions in event_reactions_list:
            for event_reaction in event_reactions:
                events = kb.out(event_reaction.id, KBEdgeType.REACTION, direction=KBEdgeDirection.IN)
                for event in events:
                    self.set_weight(event_reaction.data['name'], event.data['name'], 1.0)
                    print(event_reaction.data['name'], event.data['name'])


def main():
    kb = KnowledgeBase(None)
    ctx = KBContext(kb)
    cid = ''
    ctx.propagate_energy(Concept.from_cid(cid), 1.0)


if __name__ == "__main__":
    main()
