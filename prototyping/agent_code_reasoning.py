from src.action_manager.module import number_to_instance as Number
from src.action_manager.module import string_to_instance as String
from src.world_model.instance import Instance
from src.world_model.module import WorldModel


main_wm = WorldModel(None)

code = """
def interact(counter: CircuitCounter):
    increment(field=EntityField(
        entity=counter,
        field_name=String("counter"),
    ))
"""

code_instance = Instance("Function", {
    "name": "interact_with_counter",
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
})

# we want to iterate over the statements and check if they do what we want.
# "what we want" is a goal
counter = main_wm.add(Instance("CircuitCounter", {
    "value": Number(0),
}, instance_id='counter'))

goal = main_wm.add(Instance("GoalMakeLeftEqualToRight", {
    "left": Instance("EntityField", {
        "entity": counter,
        "field_name": Instance("String", {
            "value": "value",
        }),
    }),
    "right": Instance("Number", {
        "value": 2,
    }),
}))

# Reasoning is a sequence of simulations that looks for ways to achieve the goal.
# We can't blindly execute simulations because of side-effects and hidden conditions.
# So the basic idea of LRD-building is the same - experiment till you find a
#   way to achieve the goal.
# The difference here is that we are now looking for the details of what the task
#   is doing and we account for that in planning.

# In order to analyse the variable values the agent needs to interpret the code instruction
#   by instruction. Running the code separately from analyzing it is not an option.
# 
main_wm.add(Instance("Context", {
    'counter': counter,
}, instance_id='ctx'))

# Next we need to copy world model in order to iterate and experiment.
test_wm = main_wm.copy()

statements = code_instance.fields.body.fields.statements
for stmt in statements:
    ctx = test_wm.get_instance('ctx')
    
    if stmt.concept_name == "InstructionIncrement":
        field = stmt.fields.field
        variable = field.fields.variable
        entity = ctx.fields[variable.fields.name]
        
        field_name = field.fields.field_name
        entity.fields[field_name.fields.value].fields.value += 1

print(main_wm.get_instance('counter').fields.value.fields.value)
print(test_wm.get_instance('counter').fields.value.fields.value)

# Apart from experimenting we need to have a plan of action.
# We want to explore all branches, not only available ones.
# We need to know which branch we want to reach and act we set new goals to achieve that branch.
# This quickly might get out of hand (deeply nested).
# Not only branches can give conditional options, sometimes the agent will need to create some instance
#   before some action is possible.
# In any case at the end we will get an option with prerequisites. 
# After that we need to combine several options, adding prerequisite satisfaction before.
# There might be conflicts, but it's way too complex for now

option = Instance("GoalReachingStepOption", {
    "function": code_instance,
    "prerequisites": [Instance("CompareInstruction", {
        "left": Instance("Variable", {
            "name": "counter",
        }),
        "right": Instance("Variable", {
            "name": "target",
        }),
    })],
})