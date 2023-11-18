from functools import partial
import os
from pprint import pprint

import agci
import src.shpat_commands
from src.knowledge_base import KnowledgeBase
from src.instance import Instance
from src.state_manager import StageManager
from src.helpers import find_associated_task

from shpat.hierarchy import StaticKBHierarchy


def parse(text, debug=False):
    # Work in progress
    structure = src.shpat_commands.parse(text, debug=debug)
    return Instance.from_dict(structure)


def run(text, kb, interpreter: agci.Interpreter):
    instance = parse(text, debug=True)
    run_action(instance, kb, interpreter)


def run_action(instance, kb, interpreter: agci.Interpreter):
    func_name, new_instance = find_associated_task(kb, instance)
    interpreter.run_function(func_name, {
        **new_instance.fields
    })


def get_interpreter():
    kb = KnowledgeBase()
    hierarchy = StaticKBHierarchy(kb)

    sm = StageManager(kb, hierarchy)
    
    interpreter = agci.Interpreter({
        'list': list,
        'int': int,
        'str': str,
        'float': float,
        'print': print,
        'pprint': pprint,
        'kb': kb,
        'hierarchy': hierarchy,
        'set': set,
        'isinstance': isinstance,
        'Instance': Instance,
        'None': None,
        'max': max,
        'min': min,
        'open': open,
        'os': os,
        'exit': exit,
        'Exception': Exception,
    })
    interpreter.global_vars['run'] = partial(run, kb=kb, interpreter=interpreter)
    interpreter.global_vars['run_action'] = partial(run_action, kb=kb, interpreter=interpreter)

    interpreter.load_file("agent_code/core.py")
    interpreter.load_file("agent_code/constants.py")
    interpreter.load_file("agent_code/evaluate.py")
    interpreter.load_file("agent_code/file_system.py")
    
    return interpreter


def main():
    interpreter = get_interpreter()
    interpreter.run_main()


if __name__ == '__main__':
    main()
