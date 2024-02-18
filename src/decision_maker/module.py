import ast
from src.base_module import AgentModule
from src.knowledge_base.module import KBEdgeType, KnowledgeBase
from src.world_model import Instance
from agci.sst import Graph, ast_to_sst


class DecisionMaker(AgentModule):
    def __init__(self, core) -> None:
        super().__init__(core)
        self.plan: Graph = Graph([], [])
    
    def on_event(self, event: Instance):
        reaction: Instance = self._find_event_reaction(event)
        self.build_plan(reaction)
    
    def _find_event_reaction(self, event: Instance) -> Instance:
        kb: KnowledgeBase = self.core.knowledge_base
        concept = kb.find_concept(event.concept_name)
        reactions = kb.out(concept.id, KBEdgeType.REACTION)
        if reactions:
            return Instance(
                concept_name=reactions[0].data['name'],
            )
            
        raise ValueError("No reaction found")
    
    def build_plan(self, reaction: Instance):
        kb: KnowledgeBase = self.core.knowledge_base
        concept = kb.find_concept(reaction.concept_name)
        tasks = kb.out(concept.id, KBEdgeType.TASK)
        func_name = tasks[0].data['name']
        
        func = self.core.action_manager.interpreter.global_vars[func_name]
        new_plan = func.graph
        
        if not self.plan.get_nodes():
            self.plan = new_plan
        else:
            breakpoint()
            pass
