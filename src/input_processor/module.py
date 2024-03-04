from src.base_module import AgentModule
from src.world_model import Instance


class InputProcessor(AgentModule):
    started = False
    
    def __init__(self, core) -> None:
        super().__init__(core)

    def send_event(self, event: Instance):
        self.core.decision_maker.on_event(event)
    
    def step(self):
        pass