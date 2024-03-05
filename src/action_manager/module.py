import agci
import agci.interpreter

from src.base_module import AgentModule
from src.knowledge_base.concept import Concept
from src.knowledge_base.hierarchy import PlainHierarchy, is_child
from src.world_model.instance import Instance
from src.world_model.wm_entities import InstanceReference


HIERARCHY = PlainHierarchy()


class InterpreterWithConceptDispatch(agci.StepInterpreter):
    def __init__(self, global_vars: dict[str, any], core):
        super().__init__(global_vars)
        self.core = core
    
    def dispatch_check_param_types(self, param_type, arg_value):
        if isinstance(arg_value, InstanceReference):
            arg_value = self.core.world_model.get_instance(arg_value.instance_id)
            
        assert isinstance(arg_value, Instance)
        
        arg_concept = arg_value.get_concept()
        param_concept = Concept.from_cid(param_type)
        
        return is_child(HIERARCHY, arg_concept, param_concept), arg_value


class ActionManager(AgentModule):
    def __init__(self, core) -> None:
        super().__init__(core)
        self.execution_iterator = None
        self.is_head_initialized = False
        self.interpreter = InterpreterWithConceptDispatch({
            'len': len,
            'print': print,
            'isinstance': isinstance,
            'kb': core.knowledge_base,
            'wm': core.world_model,
            'Instance': Instance,
            'Concept': Concept,
            'ValueError': ValueError,
        }, core)
        self.interpreter.load_file('./agent_code/ac_main.py')
        self.interpreter.load_file('./agent_code/ac_knowledge_base.py')
        self.done = False
        
    def step(self):
        plan = self.core.decision_maker.plan
        if not self.is_head_initialized:
            assert plan.get_nodes()
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
