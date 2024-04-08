from agci import StepInterpreter


CODE = """
def Task__delete_folder():
    print('f1: 1')
    print('f1: 2')
    print('f1: 3')
    print('f1: 4')
    print('f1: 5')
    print('f1: 6')
    print('f1: 7')
    print('f1: 8')
    print('f1: 9')
    print('f1: 10')
    print('f1: 11')
    
    
def Task__print_expression():
    print('@@@')
"""


def main():
    interpreter = StepInterpreter({
        'print': print,
    })
    interpreter.load_code(CODE)
    
    interpreter.trigger_function("Task__delete_folder")
    
    for _ in range(20):
        interpreter.step()
    
    interpreter.trigger_function("Task__print_expression")
    
    interpreter.run()


if __name__ == "__main__":
    main()
