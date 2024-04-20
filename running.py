from agci import Interpreter
from src.decision_maker.reasoning.ast_to_instances import convert as py_to_iast

CODE = """
def main():
    print(factorial(7))
    

def factorial(x):
    if x == 1:
        return x
    return x * factorial(x - 1)
"""

CODE = """
1 + 1
"""

inr = Interpreter(global_vars={'py_to_iast':py_to_iast})

#inr.load_file("agent_code/ac_code_reasoning.py")
list(inr.run_function('py_to_iast',CODE))