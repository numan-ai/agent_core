import abc



class AgentModule(abc.ABC):
    def __init__(self, core) -> None:
        from main import AgentCore
        self.core: AgentCore = core
    
    # @abc.abstractmethod
    def step(self):
        pass
