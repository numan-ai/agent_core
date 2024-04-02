import queue

from agci.sst import Graph

from prototyping.context import KBContext
from src.base_module import AgentModule
from src.knowledge_base.module import KBEdgeType, KnowledgeBase
from src.world_model import Instance


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
        self.context = KBContext(core.knowledge_base)
    
    def on_event(self, event: Instance):
        self.event_queue.put(event)
        
    def step(self):
        if self.event_queue.empty():
            return
        event: Instance = self.event_queue.get()
        # reaction: Instance = self._find_event_reaction(event)
        # self.build_plan(None, event)
        self.context.add_energy(event.concept_name, energy=1.0, propagation=0.6)
        
        result = self.context.lookup(event.concept_name, depth=5, depth_decay=0.75)
        
        for node, weight in result:
            if self.context.hierarchy.is_subconcept(node, "Task"):
                event_reaction = self.core.knowledge_base.find_concept(node)
                task = self.core.knowledge_base.out(event_reaction.id, KBEdgeType.TASK)[0]
                self.core.action_manager.interpreter.trigger_function(
                    task.data['name'],
                    **event.fields.get_all_fields(),
                )
                print("found", node, weight)
                break
        else:
            raise ValueError("No reaction to event found")
    
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
        
        # kb: KnowledgeBase = self.core.knowledge_base
        # concept = kb.find_concept(reaction.concept_name)
        # tasks = kb.out(concept.id, KBEdgeType.TASK)
        # func_name = tasks[0].data['name']
        # breakpoint()
        
        # func = self.core.action_manager.interpreter.global_vars[func_name]
        # new_plan, new_kwargs = func.resolve_dispatch([], kwargs)
        
        task = self.core.action_manager.eagci.find_max_energy_node()
        self.core.action_manager.interpreter.trigger_function(task.node_id)
        
        self.core.action_manager.interpreter.add_context({
            **self.core.action_manager.interpreter.global_vars,
            **kwargs,
        })
        
        # if not self.plan.get_nodes():
        #     self.plan = new_plan
        # else:
        #     raise NotImplementedError("Appending plans is not implemented")
