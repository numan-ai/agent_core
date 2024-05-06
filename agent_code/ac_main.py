def react_on_user_message(sentence: AchieveGoal):
    print(dispatch_test(Number(1)))
    
    
def dispatch_test(abc: String):
    print("String")
    return 1
    
    
def dispatch_test(abc: Number):
    print("Number")
    return 2
    
    
def react_on_user_message(sentence: IsQuestionStatement):
    expression = sentence.fields.expression
    result = evaluate_expression(expression)
    print(result)

    
def react_on_user_message(sentence: IsAStatement):
    node_id1 = upsert_kb_concept(
        concept_id=sentence.fields.left.concept_name,
    )
    node_id2 = upsert_kb_concept(
        concept_id=sentence.fields.right.concept_name,
    )
    upsert_kb_edge(
        edge_label="parent",
        start_node_id=node_id1,
        end_node_id=node_id2,
    )


def react_on_user_message(sentence: IsEntityInStateStatement):
    print(get_field(sentence.fields.entity, sentence.fields.state))


def react_on_user_message(sentence: LogicOfActionStatement):
    print(sentence)


def react_on_user_message(sentence: ActOnReferencedEntityStatement(reference=DefiniteEntityReference)):
    # resolve "the button" to an entity
    entity = resolve_reference(sentence.fields.reference)
    # act on the entity
    act_on_entity(entity, sentence.fields.act)
    
    
def react_on_user_message(sentence: ActOnReferencedEntityStatement(reference=IndefiniteEntityReference)):
    act_on_entity_class(sentence.fields.act, sentence.fields.reference.fields.ref_class)


def act_on_entity_class(act: CreateAct, entity_class: CircuitButtonClass):
    api.create("Button")
    print('done')


def react_on_user_message(sentence: Act_IOT_Act):
    # add LRD nodes to KB
    pass


def react_on_user_message(sentence: HowManyThereAreQuestion(concept=PluralConcept)):
    # it's wrapped in PluralConcept, so we need to get the inner concept
    class_concept = sentence.fields.concept.fields.concept
    # ButtonClass -> Button
    instance_concept = find_instance_concept_for_class_concept(class_concept)
    # get all instances of the class
    instances = list_world_model_instances(instance_concept)
    print(len(instances))


def find_instance_concept_for_class_concept(concept: Concept):
    return Instance(concept.concept_name.replace("Class", ""))


def list_world_model_instances(concept: Concept):
    nodes = []
    
    results = wm.associative_graph.lookup(concept.concept_name)
    for result in results:
        instance = wm.get_instance(result[0])
        nodes.append(instance)
    
    return nodes

    # for node in wm.nodes:
    #     if not isinstance(node, Instance):
    #         continue
    #     if node.concept_name == concept.concept_name:
    #         nodes.append(node)
            
    # return nodes


def act_on_entity(entity: CircuitButton, act: PressAct):
    # send the "Press" action to the real world button
    api.interact(entity.fields.id, "Press")


def act_on_entity(entity: CircuitSwitch, act: PressAct):
    # send the "Press" action to the real world switch
    api.interact(entity.fields.id, "Press")


def resolve_reference(reference: DefiniteEntityReference):
    class_concept = reference.fields.ref_class
    instance_concept = find_instance_concept_for_class_concept(class_concept)
    results = wm.associative_graph.lookup(instance_concept.concept_name)
    if len(results) == 0:
        raise ValueError("Reference resolution failed")
    instance = wm.get_instance(results[0][0])
    return instance
    
    # fake entity resolution
    # return Instance("Button", {"id": 0})


def process_act_on_entity_event(entity: CircuitButton, act: PressAct):
    model_act_on_entity(entity, act)
    
    
def act_on_entity(entity: LED, act: TurnOnAct):
    goal = Instance("GoalFieldEqual", {
        "instance": Instance("InstanceField", {
            "instance": entity,
            "field": "is_on",
        }),
        "value": Instance("Boolean", {
            "value": True,
        }),
    })
    goal = traverse_lrd(goal)

    act_on_entity(
        act=Instance(goal.fields.action),
        entity=goal.fields.instance,
    )


def model_act_on_entity(entity: CircuitButton, act: PressAct):
    current_value = get_field(entity, String("output_pin"))
    new_value = current_value + 1
    set_field(entity, String("output_pin"), new_value)


# def model_act_on_entity(entity: CircuitButton, act: PressAct):
#     pin = get_field(entity, String("output_pin"))
#     set_field(pin, String("value"), Number(1))


def get_field(entity: CircuitLED, field: StateTurnedOn):
    pin = get_field(entity, String("input_pin"))
    pin_value = get_field(pin, String("value"))
    return is_equal(pin_value, Number(1))


def get_field(entity: CircuitSwitch, field: StateTurnedOn):
    return entity.fields.output_pin.fields.value.fields.value == 1


def get_field_a(entity: CircuitLED, field: StateTurnedOn):
    return entity.fields.input_pin.fields.value.fields.value == 1


def evaluate_expression(expression: BinaryMathExpression(op=GreaterThan, left=Number, right=Number)):
    return expression.fields.left.fields.value > expression.fields.right.fields.value


def evaluate_expression(expression: BinaryMathExpression(op=LessThan, left=Number, right=Number)):
    return expression.fields.left.fields.value < expression.fields.right.fields.value


def act_on_entity(entity: CircuitLED, act: PutIntoStateAct(state=TurnOnState)):
    # achieve_state_goal(entity=entity, state=act.fields.state)
    goal = Instance("GoalFieldEqual", {
        "instance": Instance("InstanceField", {
            "instance": eneity,
            "field": "is_on",
        }),
        "value": Instance("Boolean", {
            "value": True,
        }),
    })
    goal = traverse_lrd(goal)

    act_on_entity(
        act=Instance(goal.fields.action),
        entity=goal.fields.instance,
    )


def achieve_state_goal(entity: CircuitLED, state: TurnedOnState):
    field_node = kb_find_field_node(entity=entity, concept=state)
    task_node = kb.out(field_node.id, KBEdgeType.FIELD_GETTER)[0]
    task_name = task_node.data['name']
    func_entity = interpreter.global_vars[task_name]
    graph = func_entity.dispatch_options[0].graph
    print(graph)
    # debug(graph)
    
    graph_instance = Instance("AGCI_Return", {
        "value": Instance("AGCI_CompareOperation", {
            "left": Instance("AGCI_GetField", {
                "entity": entity,
                "field_name": Instance("String", {
                    "value": "input_pin",
                }),
            }),
            "right": Instance("Number", {
                "value": 1,
            }),
        }),
    })
    
    goal_instance = Instance("GoalMakeLeftEqualToRight", {
        "left": Instance("EntityField", {
            "entity": entity,
            "field_name": Instance("String", {
                "value": "input_pin",
            }),
        }),
        "right": Instance("Number", {
            "value": 1,
        }),
    })
    
    achieve_linear_goal(goal=goal_instance)
    

def achieve_linear_goal(goal: GoalMakeLeftEqualToRight):
    right_value = evaluate(goal.fields.right)
    
    while True:
        left_value = evaluate(goal.fields.left)
        
        distance = measure_linear_goal_distance(left_value, right_value)
        print('distance', distance)
        
        if distance == 0:
            return
        if distance < 0:
            increase(goal.fields.left)
        else:
            decrease(goal.fields.left)


def measure_linear_goal_distance(left_value: Number, right_value: Number):
    return left_value.fields.value - right_value.fields.value


def increase(expression: EntityField):
    raise NotImplementedError()
    # set_field(expression.fields.entity, expression.fields.field_name, Instance("Number", {
    #     "value": 1,
    # }))


def evaluate(expression: EntityField):
    return evaluate(expression.fields.entity.fields[
        expression.fields.field_name.fields.value
    ])


def kb_find_field_node(entity: CircuitLED, concept: TurnedOnState):
    concept_node = kb.find_concept(entity.concept_name)
    fields = kb.out(concept_node.id, KBEdgeType.FIELD_NODE)
    for field in fields:
        field_concept = kb.out(field.id, KBEdgeType.FIELD_CONCEPT)[0]
        if field_concept.data['name'] == concept.concept_name:
            return field
        
    raise ValueError("Field not found")


def model_wire_step(wire: CircuitWire):
    pin_a = get_field(wire, String("pin_a"))
    pin_a_value = get_field(pin_a, String("value"))
    pin_b = get_field(wire, String("pin_b"))
    pin_b_value = get_field(pin_b, String("value"))
    wire_value = max(pin_a_value, pin_b_value)
    set_field(pin_a, String("value"), wire_value)
    set_field(pin_b, String("value"), wire_value)


def react_on_user_message(sentence: GreetingStatement):
    print("Hello!")


def evaluate(expression: BinaryMathExpression(sign=PlusSign)):
    left = evaluate(expression.fields.left)
    right = evaluate(expression.fields.right)
    return Number(left.fields.value + right.fields.value)


def evaluate(expression: BinaryMathExpression(sign=MinusSign)):
    left = evaluate(expression.fields.left)
    right = evaluate(expression.fields.right)
    return Number(left.fields.value - right.fields.value)


def evaluate(expression: BinaryMathExpression(sign=MultiplicationSign)):
    left = evaluate(expression.fields.left)
    right = evaluate(expression.fields.right)
    return Number(left.fields.value * right.fields.value)


def evaluate(expression: BinaryMathExpression(sign=DivisionSign)):
    left = evaluate(expression.fields.left)
    right = evaluate(expression.fields.right)
    return Number(left.fields.value / right.fields.value)


def evaluate(expression: BinaryMathExpression(sign=GreaterThanSign)):
    left = evaluate(expression.fields.left)
    right = evaluate(expression.fields.right)
    return Boolean(left.fields.value > right.fields.value)


def evaluate(expression: BinaryMathExpression(sign=LessThanSign)):
    left = evaluate(expression.fields.left)
    right = evaluate(expression.fields.right)
    return Boolean(left.fields.value < right.fields.value)


def evaluate(expression: Number):
    return Number(float(expression.fields.value))


def evaluate(expression: NegativeNumber):
    return Number(-float(expression.fields.number.fields.value))


def evaluate(expression: FloatingPointNumber):
    return Number(float(str(expression.fields.before_dot.fields.value) + '.' + str(expression.fields.after_dot.fields.value)))
   

def evaluate(expression: MathExpressionInParenthesis):
    val = evaluate(expression.fields.expression)
    return val
 

def react_on_user_message(sentence: PrintMathExpression):
    result = evaluate(sentence.fields.expression)
    print(result.fields.value)
    
    
def react_on_user_message(sentence: BinaryMathExpression):
    result = evaluate(sentence)
    print(result.fields.value)


def act_on_entity(act: PressAction, entity: Button):
    api.press(entity.fields.id)
    print('pressing the button')


def act_on_entity(act: PressAction, entity: Switch):
    api.press(entity.fields.id)
    print('pressing the switch')
