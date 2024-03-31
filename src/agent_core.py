
from src.input_processor import InputProcessor
from src.decision_maker import DecisionMaker
from src.action_manager import ActionManager
from src.world_model import WorldModel
from src.knowledge_base import KnowledgeBase
from src.unified_graph.graph import UGraph


class AgentCore:
    def __init__(self):
        self.knowledge_base = KnowledgeBase(self)
        self.input_processor = InputProcessor(self)
        self.decision_maker = DecisionMaker(self)
        self.world_model = WorldModel(self)
        self.action_manager = ActionManager(self)
        
        # self.ugi = UGraph(
        #     knowledge_base=self.knowledge_base,
        #     world_model=self.world_model,
        #     ac_graph=self.action_manager.interpreter.combined_graph,
        # )
        # self.action_manager.interpreter.global_vars["ugi"] = self.ugi
        
        self.modules = [
            self.input_processor,
            self.decision_maker,
            self.action_manager,
            self.world_model,
            self.knowledge_base,
        ]
        
    def step(self, world=None):
        for module in self.modules:
            module.step()
        
        if world is not None:
                world.step()
            
    def run(self, world=None):
        while not self.action_manager.done:
            self.step(world=world)
