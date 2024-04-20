from saving_loading import load
from graph_lib import Graph

graph = Graph([], [])

#graph.nodes, graph.edges = load("LRDS/and_gate.json")
#goals = ["led_on == True"]

#graph.nodes, graph.edges = load("LRDS/bluetooth.json")
#goals = ["led_on == True"]

graph.nodes, graph.edges = load("LRDS/or_gate.json")
goals = ["led_on == True"]

actions = []


#       [ - 1 ]   |   Rename all attributes so they're unique
for node in graph.nodes:
    if node.node_type == "attribute":
        main_id = graph.node_in_edges(node.id)[0].from_id
        node.name = graph.get_node_by_id(main_id).name.replace(" ", "_") + "_" + node.name.replace(" ", "_")


#       [  0  ]   |   Assign variables
attributes = [node for node in graph.nodes if node.node_type == "attribute"]
for attribute in attributes:
    exec(f"{attribute.name} = {attribute.value}")


#       [ 0.5 ]   |   Replace function placeholders
for node in graph.nodes:
    if "function" in node.node_type:
        variable_edges = [edge for edge in graph.node_in_edges(node.id) if edge.name == "x"]
        variable_node = graph.get_node_by_id(variable_edges[0].from_id)
        placeholder_name = variable_node.name
        node.name = node.name.replace("x", placeholder_name)

        # We can't forget about function node's associated consequences

        if (consequence_edge := graph.node_out_edges(node.id)[0]).name == "con":
            consequence_node = graph.get_node_by_id(consequence_edge.to_id)
            consequence_node.name = consequence_node.name.replace("x", placeholder_name)

RUNNING = 1
while RUNNING:
    #print("Goal:", goal)
#       [  1  ]   |   Check if the goal has been achieved
    #condition = False
    #exec(f"if {goal}: condition = True")
    #if condition:
    #    print("We're done")
    #    break

    for i, goal in enumerate(goals):
    #       [ 2.1 ]   |   Find a consequence that matches the goal
        for node in graph.nodes:
            if node.name == goal and node.node_type == "consequence":
                print(f"{node.name} matches the goal")



    #       [ 2.2 ]   |   What function provokes that consequence
                causing_edge = graph.node_in_edges(node.id)[0]
                causing_function = graph.get_node_by_id(causing_edge.from_id)


    #       [  3  ]   |   Explore 1 pvk edge
        normal = 1
        in_edges = [edge for edge in graph.node_in_edges(causing_function.id) if "pvk" in edge.name]
        if (x := len(in_edges)) > 1:
            raise NotImplementedError("Can't have multiple pvk connections yet")
        elif x == 1:
            in_edge = in_edges[0]
            in_node = graph.get_node_by_id(in_edge.from_id)
        elif x == 0:
            in_edge = [edge for edge in graph.node_in_edges(causing_function.id) if "out" in edge.name][0]
            in_node = graph.get_node_by_id(in_edge.from_id)

            # Evaluating logic gate

            if in_node.name == "and": # And we want it to be true
                inputs = [edge for edge in graph.node_in_edges(in_node.id)]
                if_functions = [graph.get_node_by_id(input_i.from_id) for input_i in inputs]
            elif in_node.name == "or":
                inputs = [edge for edge in graph.node_in_edges(in_node.id)]
                if_functions = [graph.get_node_by_id(input_i.from_id) for input_i in inputs]


            # # #

            normal = 0

        goals.pop(i)
        if normal:
            if in_node.node_type == "if_function":
                goals.append(in_node.name)
            else:
                actions.append(in_edge)
        else:
            goals.extend([if_function.name for if_function in if_functions])

        if not goals:
            RUNNING = False


#       [  5  ]   |   Show plan
acts = [act.name.replace("pvk ","") for act in actions]
print("plan:", acts[::-1])