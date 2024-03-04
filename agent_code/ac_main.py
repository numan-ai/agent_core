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
    

def react_on_user_message(sentence: ActOnReferencedEntityStatement):
    # resolve "the button" to an entity
    entity = resolve_reference(sentence.fields.reference)
    # act on the entity
    act_on_entity(entity, sentence.fields.act)
    
    
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
    
    
def act_on_entity(entity: Button, act: PressAct):
    # send the "Press" action to the real world button
    api.interact(entity.fields.id, "Press")
    

def resolve_reference(reference: DefiniteEntityReference):
    # fake entity resolution
    return Instance("Button", {"id": 0})


def process_act_on_entity_event(entity: Button, act: PressAct):
    entity.fields.output_pin.fields.value = 1
    set_field(entity, "OutputPin", 1)
    set_field(entity, "output_pin", 1)
    set_field(FieldOfEntity(entity, "OutputPin"), 1)


def process_act_on_entity_event(entity: LED, act: PressAct):
    pass


def set_field(field: FieldOfEntity, value: Concept):
    pass


def get_field(entity: LED, field: StateTurnedOn):
    return entity.fields.input_pin.fields.value == 1


def evaluate_expression(expression: BinaryMathExpression(op=GreaterThan, left=Number, right=Number)):
    return expression.fields.left.fields.value > expression.fields.right.fields.value


def evaluate_expression(expression: BinaryMathExpression(op=LessThan, left=Number, right=Number)):
    return expression.fields.left.fields.value < expression.fields.right.fields.value
