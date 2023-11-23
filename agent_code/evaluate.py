# def get_field(entity, field_name):
#     if field_name not in entity.fields:
#         print('Field not found: ' + field_name)
#         concept = kb.find_concept(Concept.from_uid(entity.concept).name)
#         fields = kb.out(concept.id, 'fields')
#         for field in fields:
#             if field.data['name'] == field_name:
#                 fex_tasks = kb.out(field.id, 'fex_out')
#                 fex_task_name = fex_tasks[0].data['name']
#                 fex_task = __agci.ctx[-1].variables[fex_task_name]
#                 print('Field triggered fex function: ' + fex_task_name)
#                 value = fex_task(entity)
#                 entity.fields[field_name] = value
#                 break
#     return entity.fields[field_name]


def evaluate_constant(expr):
    return expr


def evaluate_sum(left, op, right):
    left_value = get_field(left, 'value')
    right_value = get_field(right, 'value')
    return Instance("Number", {
        "value": left_value + right_value
    })


def evaluate_difference(left, op, right):
    left_value = get_field(left, 'value')
    right_value = get_field(right, 'value')
    return Instance("Number", {
        "value": left_value - right_value
    })


def evaluate_multiplication(left, op, right):
    left_value = get_field(left, 'value')
    right_value = get_field(right, 'value')
    return Instance("Number", {
        "value": left_value * right_value
    })


def evaluate_division(left, op, right):
    left_value = get_field(left, 'value')
    right_value = get_field(right, 'value')
    return Instance("Number", {
        "value": left_value / right_value
    })


def evaluate_contains(left, op, right):
    left_value = get_field(left, 'value')
    right_value = get_field(right, 'value')
    return Instance("Boolean", {
        "value": right_value in left_value
    })


def evaluate_comparison_gt(left, op, right):
    left_value = get_field(left, 'value')
    right_value = get_field(right, 'value')
    return Instance("Boolean", {
        "value": left_value > right_value
    })


def evaluate_comparison_lt(left, op, right):
    left_value = get_field(left, 'value')
    right_value = get_field(right, 'value')
    return Instance("Boolean", {
        "value": left_value < right_value
    })


def evaluate_comparison_isnt_gt(left, op, right):
    left_value = get_field(left, 'value')
    right_value = get_field(right, 'value')
    return Instance("Boolean", {
        "value": left_value < right_value
    })


def evaluate_comparison_isnt_lt(left, op, right):
    print('left')
    left_value = get_field(left, 'value')
    print('right')
    right_value = get_field(right, 'value')
    return Instance("Boolean", {
        "value": left_value > right_value
    })


def evaluate_expression(expr):
    left = run_query("evaluate", {
        "expr": get_field(expr, 'left')
    })
    right = run_query("evaluate", {
        "expr": get_field(expr, 'right')
    })
    result = run_query("evaluate_atomic", {
        "right": right,
        "op": get_field(expr, 'op'),
        "left": left,
    })
    return result


def evaluate_field_expression(expr):
    entity = get_field(expr, 'entity')
    if entity.concept == 'FieldExpression' or entity.concept == 'ItPointer':
        entity = run_query("evaluate", {
            "expr": entity,
        })
    result = run_query("get", {
        "field": get_field(expr, 'field'),
        "entity": entity,
    })
    return result


def evaluate_it_pointer(expr):
    return get_it_pointer()


def get_entity_field(field, entity):
    field_name = get_field(field, 'value')
    return get_field(entity, field_name)


def run_command_on_list(command):
    lst = get_field(command, 'list')
    for item in get_field(lst, 'value'):
        run_query(get_field(command, 'command'), {
            "object": item,
        })


def run_command_on_list_with_filter(command):
    lst = get_field(command, 'list')
    for item in get_field(lst, 'value'):
        set_it_pointer(item)
        filter_result = run_query("evaluate", {
            "expr": get_field(command, 'filter'),
        })
        if get_field(filter_result, 'value'):
            run_query(get_field(command, 'command'), {
                "object": item,
            })


def print_expression(object):
    value = run_query("evaluate", {
        "expr": object,
    })
    run_query("print", {
        "object": value,
    })


def evaluate_maximum_expression(expr):
    lst = get_field(expr, 'list')
    objs = []
    for obj in get_field(lst, 'list'):
        value = run_query("evaluate", {
            "expr": obj,
        })
        objs.append(get_field(value, 'value'))
    return Instance("Number", {"value": max(objs)})


def evaluate_bracketed_math_expression(expr):
    expr = get_field(expr, 'expr')
    return run_query('evaluate', {
        'expr': expr,
    })
