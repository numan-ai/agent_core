from src.input_processor import InputProcessor
from src.decision_maker import DecisionMaker
from src.action_manager import ActionManager
from src.world_model import WorldModel
from src.knowledge_base import KnowledgeBase


class AgentCore:
    def __init__(self):
        self.input_processor = InputProcessor(self)
        self.decision_maker = DecisionMaker(self)
        self.action_manager = ActionManager(self)
        self.world_model = WorldModel(self)
        self.knowledge_base = KnowledgeBase(self)
        
        self.modules = [
            self.input_processor,
            self.decision_maker,
            self.action_manager,
            self.world_model,
            self.knowledge_base,
        ]
        
    def step(self):
        for module in self.modules:
            module.step()


def main():
    core = AgentCore()
    for _ in range(10):
        core.step()
    


if __name__ == "__main__":
    main()
