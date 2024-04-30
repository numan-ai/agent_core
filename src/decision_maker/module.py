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
