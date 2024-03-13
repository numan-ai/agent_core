def react_on_user_message(sentence: AchieveGoal):
    achieve_goal(goal=sentence.fields.goal)


def achieve_goal(goal: GoalMakeLeftEqualToRight(left=EntityField, right=Number)):
    options = find_options()
    print(options)
    goal = wm.add(goal)
    
    for _ in range(40):
        test_wm = wm.copy()
        
        while True:
            test_goal = test_wm.get_instance(goal.id)
            old_distance = get_linear_goal_distance(test_goal)
            option = random.choice(options)
            
            apply_option(test_wm, test_goal, option)
            new_distance = get_linear_goal_distance(test_goal)
            if new_distance >= old_distance:
                break
        
        new_distance = get_linear_goal_distance(test_goal)
        
        if new_distance == 0:
            print('Goal reached!')
            return True
        print('nd', new_distance)
    
    return False
        

def apply_option(test_wm, goal, option):
    ctx = test_wm.add(Instance("Context", {
        "counter": goal.fields.left.fields.entity,
        "target": Number(0),
    }))
    code = option.fields.function
    
    for instruction in code.fields.body:
        acr_run_instruction(ctx, instruction)
    
    
def acr_run_instruction(ctx: Context, inst: BranchInstruction):
    test_result = acr_run_instruction(ctx, inst.fields.test)
    if test_result:
        for true_inst in inst.fields.true_branch:
            acr_run_instruction(ctx, true_inst)
    else:
        for false_inst in inst.fields.false_branch:
            acr_run_instruction(ctx, false_inst)


def acr_run_instruction(ctx: Context, inst: CompareInstruction):
    left = acr_evaluate(ctx, inst.fields.left)
    right = acr_evaluate(ctx, inst.fields.right)
    return left.fields.value == right.fields.value


def acr_run_instruction(ctx: Context, inst: InstructionIncrement(field=VariableField)):
    field = inst.fields.field
    entity = ctx.fields[field.fields.variable.fields.name]
    entity.fields[field.fields.field_name.fields.value] += 1
    

def acr_evaluate(ctx: Context, value: Variable):
    return ctx.fields[value.fields.name]


def acr_evaluate(ctx: Context, value: Number):
    return value


def check_condition():
    pass
        
        
def get_linear_goal_distance(goal: GoalMakeLeftEqualToRight):
    left = evaluate(goal.fields.left)
    right = evaluate(goal.fields.right)
    return abs(left.fields.value - right.fields.value)
    
    
def find_options():
    # the problem now is that we need to call a function
    #   with parameters, but in order to understand which parameter to pass
    #   we need to traverse the code from the change we want to where
    #   we want to apply it
    # Another problem is that we might need to provide some other params
    
    # Another problem - prerequisite arguments might change inside the function
    #   as it executes. So prerequisites are not the "compare instructions",
    
    code_instance1 = parse_code()
    option1 = Instance("GoalReachingStepOption", {
        "function": code_instance1,
        "prerequisites": [
            Instance("CompareInstruction", {
                "left": Instance("Variable", {
                    "name": "counter",
                }),
                "right": Instance("Variable", {
                    "name": "target",
                }),
            }),
        ],
        "params": [
            # ...
        ]
    })
    code_instance2 = parse_code2()
    
    option2 = Instance("GoalReachingStepOption", {
        "function": code_instance2,
        "prerequisites": [
            Instance("CompareInstruction", {
                "left": Instance("Variable", {
                    "name": "counter",
                }),
                "right": Instance("Variable", {
                    "name": "target",
                }),
            }),
        ],
        "params": [
            # ...
        ]
    })
    return [option1, option2]
    

def parse_code():
    code_instance = wm.add(Instance("Function", {
        "name": "interact_with_counter",
        "params": [
            Instance("FunctionParam", {
                "name": "counter",
                "concept": "CircuitCounter",
            }),
        ],
        "body": [
            Instance("BranchInstruction", {
                "test": Instance("CompareInstruction", {
                    "left": Instance("Variable", {
                        "name": "counter",
                    }),
                    "right": Instance("Variable", {
                        "name": "target",
                    }),
                }),
                "true_branch": [
                    Instance("InstructionIncrement", {
                        "field": Instance("VariableField", {
                            "variable": Instance("Variable", {
                                "name": "counter",
                            }),
                            "field_name": Instance("String", {
                                "value": "value",
                            }),
                        }),
                    }),
                ],
                "false_branch": [],
            }),
        ],
    }))
    return code_instance




def parse_code2():
    code_instance = wm.add(Instance("Function", {
        "name": "interact_with_counter",
        "params": [
            Instance("FunctionParam", {
                "name": "counter",
                "concept": "CircuitCounter",
            }),
        ],
        "body": [
            Instance("BranchInstruction", {
                "test": Instance("CompareInstruction", {
                    "left": Instance("Variable", {
                        "name": "counter",
                    }),
                    "right": Instance("Number", {
                        "value": 1,
                    })
                }),
                "true_branch": [
                    Instance("InstructionIncrement", {
                        "field": Instance("VariableField", {
                            "variable": Instance("Variable", {
                                "name": "counter",
                            }),
                            "field_name": Instance("String", {
                                "value": "value",
                            }),
                        }),
                    }),
                ],
                "false_branch": [],
            }),
        ],
    }))
    return code_instance
