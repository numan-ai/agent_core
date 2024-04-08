import ast

from agci import StepInterpreter

from src.decision_maker.reasoning.ast_to_iast import iast_convert
from src.knowledge_base.concept import Concept
from src.knowledge_base.hierarchy import is_child
from src.world_model.instance import Instance
from src.action_manager.module import HIERARCHY, string_to_instance as String
from src.action_manager.module import number_to_instance as Number
from src.world_model.wm_entities import InstanceReference


class DispatchStepInterpreter(StepInterpreter):
    def dispatch_check_param_types(self, param_type, arg_value):
        if isinstance(arg_value, InstanceReference):
            arg_value = self.core.world_model.get_instance(arg_value.instance_id)
            
        if isinstance(arg_value, (float, int)):
            arg_value = Instance("Number", {"value": arg_value})
            
        if isinstance(arg_value, str):
            arg_value = Instance("String", {"value": arg_value})
            
        assert isinstance(arg_value, Instance)
        
        arg_concept = arg_value.get_concept()
        param_concept = Concept.from_cid(param_type)
        
        return is_child(HIERARCHY, arg_concept, param_concept), arg_value


def call_with_kwargs(callable, args, kwargs):
    """ Call function with args and kwargs.
    AGCI does not support star args and kwargs. 
    This function is a workaround for that.
    """
    return callable(*args, **kwargs)


IAST_CODE = """
def main():
    if a > 10:
        print(i)
"""


def main():
    iast_code = iast_convert(ast.parse(IAST_CODE).body[0])
    
    interpreter = DispatchStepInterpreter({
        "Instance": Instance,
        "Number": Number,
        "String": String,
        "iast_code": iast_code,
        "Concept": Concept,
        
        "print": print,
        "range": range,
        "call_with_kwargs": call_with_kwargs,
        "is_subconcept": HIERARCHY.is_subconcept,
    })
    interpreter.load_file("agent_code/ac_code_reasoning.py")
    interpreter.run_main()


if __name__ == "__main__":
    main()
