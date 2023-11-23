def main():    
    run("print 123")
    # run_action(Instance("ActOnEntity", {
    #     "act": Instance("RemoveAct", {}),
    #     "entity": Instance("File", {
    #         "path": Instance("FileSystemPath", {
    #             "value": "main.txt",
    #         }),
    #     }),
    # }))


def print_constant():
    constant = resolve("the constant")
    print(get_field(constant, 'value'))


def print_expression():
    value = run('evaluate the expression')
    print(value)


def evaluate_binary_math_expression_plus(object):
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left + right
    return result


def evaluate_binary_math_expression_minus(object):
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left - right
    return result


def evaluate_binary_math_expression_multiply(object):
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left * right
    return result


def evaluate_binary_math_expression_divide(object):
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left / right
    return result


def evaluate_greater_comparison_expression(object):
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left > right
    return result


def evaluate_less_comparison_expression(object):
    left = run('evaluate the left expression')
    right = run('evaluate the right expression')
    result = left < right
    return result


def evaluate_constant(object):
    return get_field(object, 'value')


def process_user_imperative(user_says):
    # action = run("find the action of the imperative")
    
    action = run_action(Instance("ActionWithExtension", {
        "action": Instance("ActionOnEntityReference", {
            "action": Instance("FindActionInstance"),
            "entity": Instance("DefiniteEntityReference", {
                "referent": Instance("Concept", {
                    "name": "Action",
                })
            })
        }),
        "extension": Instance("ExtensionOf", {
            "of": Instance("DefiniteEntityReference", {
                "referent": Instance("Concept", {
                    "name": "Imperative",
                })
            })
        })
    }))
    
    run_action(action)


def run_action_pair():
    first_action = run("the first action")
    second_action = run("the second action")
    
    run_action(first_action)
    run_action(second_action)


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
