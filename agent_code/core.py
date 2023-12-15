def main():    
    run("print 123", by_user=True)
    # run("please don't remove any python files")
    
    # run("Hannah has an apple")
    # run_instance(Instance("ActOnEntity", {
    #     "act": Instance("RemoveAct", {}),
    #     "entity": Instance("File", {
    #         "path": Instance("FileSystemPath", {
    #             "value": "main.txt",
    #         }),
    #     }),
    # }))
    
    # run_instance(Instance("SimpleStatement", {
    #     "subject": Instance("DefiniteEntityReferenceByName", {
    #         "name": Instance("Name", {
    #             "value": "Hannah",
    #         })
    #     }),
    #     "act": Instance("HasAct"),
    #     "direct_object": Instance("IndefiniteEntityReference", {
    #         "concept": Instance("Concept", {
    #             "value": "AppleClass",
    #         }),
    #     }),
    # }))
    
    
def react_to_imperative():
    run("process the imperative")
    
    
def process_simple_statement():
    subject = resolve("the subject")
    act = resolve("the act")
    direct_object = resolve("the direct object")


def print_constant():
    constant = resolve("the constant")
    print(get_field(constant, 'value'))


def print_expression():
    value = run('evaluate the expression')
    print(value)


def evaluate_binary_math_expression_plus():
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left + right
    return result


def evaluate_binary_math_expression_minus():
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left - right
    return result


def evaluate_binary_math_expression_multiply():
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left * right
    return result


def evaluate_binary_math_expression_divide():
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left / right
    return result


def evaluate_greater_comparison_expression():
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left > right
    return result


def evaluate_less_comparison_expression():
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left < right
    return result


def evaluate_constant(object):
    return get_field(object, 'value')


def process_imperative():
    imperative = resolve("the imperative")
    action = get_field(imperative, 'act')
    run_instance(action)


def run_action_pair():
    first_action = run("the first action")
    second_action = run("the second action")
    
    run_instance(first_action)
    run_instance(second_action)


def remove_file():
    file_path = run("find the path of the file")
    run("run shell command 'rm' with the file path")


def run_bash_command():
    arguments = run("collect all arguments")
    executable = run("find the executable")
    command = executable + " " + arguments
    os.system(command)


def run_rm_command(entity):
    print('IT WORKS!', entity)
    print('IT WORKS!', entity.fields)


def run_conditional_action():
    if run("evaluate the condition"):
        run("run the action")


def run_action_on_entity_reference():
    reference = resolve("the reference")
    instance = resolve_instance(reference)
    
    this_act = resolve("the act")
    act = get_field(this_act, 'act')
    
    print('\n\n---')
    print(act)
    print(instance)
    print('---\n\n')
    
    run_instance(Instance("ActOnEntity", {
        "act": act,
        "entity": instance,
    }))