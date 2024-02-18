import agci
import agci.interpreter

from src.base_module import AgentModule


class ActionManager(AgentModule):
    def __init__(self, core) -> None:
        super().__init__(core)
        self.execution_iterator = None
        self.is_head_initialized = False
        self.interpreter = agci.StepInterpreter({
            'print': print
        })
        self.interpreter.ctx.append(agci.interpreter.InterpreterContext(
            variables={**self.interpreter.global_vars}
        ))
        self.interpreter.load_file('./agent_code/main.py')
        self.done = False
        
    def step(self):
        plan = self.core.decision_maker.plan
        if not self.is_head_initialized and plan.get_nodes():
            self.head = plan.get_nodes()[0]
            self.execution_iterator = self.interpreter.interpret_node(plan, self.head)
            self.is_head_initialized = True
            
        if self.head is None:
            self.done = True
            return
        
        try:
            next(self.execution_iterator)
        except StopIteration as e:
            result, self.head = e.value
            self.execution_iterator = self.interpreter.interpret_node(plan, self.head)
