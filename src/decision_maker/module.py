import ast
from src.base_module import AgentModule
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
        return event
    
    def build_plan(self, reaction: Instance):
        func = f"""
def main():
    print({reaction.fields['sentence'].fields['act'].fields['entity'].fields['left'].fields['value']} + 2)
    print(1 + 4)
        """
        func_def = ast.parse(func).body[0]
        new_plan = ast_to_sst.Converter().convert(func_def)
        
        if not self.plan.get_nodes():
            self.plan = new_plan
        else:
            breakpoint()
            pass
