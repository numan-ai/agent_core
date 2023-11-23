from functools import partial
import os
from pprint import pprint

import agci
from src.interfaces.base_knowledge_base import KBEdgeType
import src.shpat_commands
from src.knowledge_base import KnowledgeBase
from src.instance import Instance
from src.state_manager import ReferenceManager
from src.helpers import find_associated_task


def parse(text, debug=False):
    # Work in progress
    structure = src.shpat_commands.parse(text, debug=debug)
    return Instance.from_dict(structure['name'], structure['data'])


def run(text, kb, interpreter: agci.Interpreter, sm: ReferenceManager):
    instance = parse(text, debug=True)
    return run_action(instance, kb, interpreter, sm=sm)


def resolve(text, stage_manager: ReferenceManager):
    instance = parse(text, debug=True)
    result = stage_manager.find(instance)
    print(f"Resolved \"{text}\" to:", result)
    return result


def get_field(entity, field_name, kb: KnowledgeBase, interpreter: agci.Interpreter):
    if field_name not in entity.fields:
        print('Field not found: ' + field_name)
        concept = kb.find_concept(entity.concept_name)
        fields = kb.out(concept.id, KBEdgeType.FIELD)
        
        for field in fields:
            if field.data['name'] != field_name:
                continue
            fex_tasks = kb.out(field.id, KBEdgeType.FEX_OUT)
            fex_task_name = fex_tasks[0].data['name']
            print('Field triggered fex function: ' + fex_task_name)
            
            value = interpreter.run_function(fex_task_name, {
                'entity': entity,
            })
            
            entity.fields[field_name] = value
            break
        else:
            raise Exception(f'Field "{field_name}" not found')
    
    return entity.fields[field_name]


def run_action(instance, kb, interpreter: agci.Interpreter, sm: ReferenceManager):
    sm.push_context()
    sm.save(instance)
    func_name, new_instance = find_associated_task(kb, instance)
    result = interpreter.run_function(func_name, {
        **new_instance.fields
    })
    sm.pop_context()
    return result
    


def get_interpreter():
    kb = KnowledgeBase()

    sm = ReferenceManager(kb)
    
    interpreter = agci.Interpreter({
        'list': list,
        'int': int,
        'str': str,
        'float': float,
        'print': print,
        'pprint': pprint,
        'kb': kb,
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
    interpreter.global_vars['run'] = partial(run, kb=kb, interpreter=interpreter, sm=sm)
    interpreter.global_vars['run_action'] = partial(run_action, kb=kb, interpreter=interpreter, sm=sm)
    interpreter.global_vars['resolve'] = partial(resolve, stage_manager=sm)
    interpreter.global_vars['get_field'] = partial(get_field, kb=kb, interpreter=interpreter)

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
