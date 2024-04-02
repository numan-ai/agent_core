from src.base_module import AgentModule
from src.world_model import Instance


def dummy_input_filter(event):
    return True


class InputProcessor(AgentModule):
    """ Processes raw data and sends events to the decision maker.
    """
    started = False
    
    def __init__(self, core) -> None:
        super().__init__(core)

    def send_event(self, event: Instance):
        if dummy_input_filter(event):
            self.core.decision_maker.on_event(event)
    
    def step(self):
        pass