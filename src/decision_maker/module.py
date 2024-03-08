import queue
import agci
from src.base_module import AgentModule
from src.knowledge_base.module import KBEdgeType, KnowledgeBase
from src.world_model import Instance
from agci.sst import Graph


class DecisionMaker(AgentModule):
    """ Takes in events and builds a plan of action. 
    Each new plan is appended at the end of the current plan.
    We might want to add an event manager module that will
        handle the logic of ignoring events that are not relevant.
    Before building a plan we are looking for a reaction for the event.
    Example of a reaction to an event:
        event: GreetingFromHuman
        reaction: GreetHuman
    Then we are looking for a task to execute the reaction.
    Reaction task is associated with a concept of the reaction with
        an edge of type REACTION.
    """
    def __init__(self, core) -> None:
        super().__init__(core)
        self.plan: Graph = Graph([], [])
        self.event_queue = queue.Queue()
    
    def on_event(self, event: Instance):
        self.event_queue.put(event)
        
    def step(self):
        if self.event_queue.empty():
            return
        event: Instance = self.event_queue.get()
        reaction: Instance = self._find_event_reaction(event)
        self.build_plan(reaction, event)
    
    def _find_event_reaction(self, event: Instance) -> Instance:
        kb: KnowledgeBase = self.core.knowledge_base
        concept = kb.find_concept(event.concept_name)
        reactions = kb.out(concept.id, KBEdgeType.REACTION)
        
        if reactions:
            return Instance(
                concept_name=reactions[0].data['name'],
            )
            
        raise ValueError("No reaction found")
    
    def build_plan(self, reaction: Instance, event: Instance):
        kwargs = event.fields.get_all_fields()
        
        kb: KnowledgeBase = self.core.knowledge_base
        concept = kb.find_concept(reaction.concept_name)
        tasks = kb.out(concept.id, KBEdgeType.TASK)
        func_name = tasks[0].data['name']
        
        func = self.core.action_manager.interpreter.global_vars[func_name]
        new_plan, new_kwargs = func.resolve_dispatch([], kwargs)
        
        self.core.action_manager.interpreter.ctx.append(
            agci.interpreter.InterpreterContext(
                variables={
                    **self.core.action_manager.interpreter.global_vars,
                    **new_kwargs,
                }
            )
        )
        
        if not self.plan.get_nodes():
            self.plan = new_plan
        else:
            breakpoint()
            pass
