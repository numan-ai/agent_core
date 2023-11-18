import os
from pprint import pprint

import agci
import shpat_commands
from shpat.hierarchy import StaticKBHierarchy
from shpat.knowledge_base import KnowledgeBase

from agent.entity import Entity
from src.state_manager import StageManager

IT_ENTITY = None


def parse(text, debug=False):
    structure = shpat_commands.parse(text, debug=debug)
    entity = Entity.from_dict(structure)
    return entity


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
        'None': None,
        'max': max,
        'min': min,
        'open': open,
        'os': os,
        'exit': exit,
        'Exception': Exception,
    })

    interpreter.load_file("agent_code/core.ipy")
    interpreter.load_file("agent_code/number.py")
    interpreter.load_file("agent_code/string.py")
    interpreter.load_file("agent_code/evaluate.py")
    interpreter.load_file("agent_code/file_system.py")
    
    return interpreter


def main():
    interpreter = get_interpreter()
    interpreter.run_main()


if __name__ == '__main__':
    main()
