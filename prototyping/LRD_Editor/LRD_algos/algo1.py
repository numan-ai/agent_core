from saving_loading import load
from graph_lib import Graph

graph = Graph([], [])

#graph.nodes, graph.edges = load("LRDS/example_sce_1.json")
#goal = "m_e_out == True"

#graph.nodes, graph.edges = load("LRDS/example_sce_2.json")
#goal = "led_on == True"

#graph.nodes, graph.edges = load("LRDS/sce1.json")
#goal = "led_on == True"

#graph.nodes, graph.edges = load("LRDS/sce2.json")
#goal = "led_on == True"

#graph.nodes, graph.edges = load("LRDS/sce3.json")
#goal = "led_on == True"

#graph.nodes, graph.edges = load("LRDS/sce4.json")
#goal = "led_on == True"

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


while 1:
    print("Goal:",goal)
#       [  1  ]   |   Check if the goal has been achieved
    condition = False
    exec(f"if {goal}: condition = True")
    if condition:
        print("We're done")
        break


#       [ 2.1 ]   |   Find a consequence that matches the goal
    for node in graph.nodes:
        if node.name == goal:


#       [ 2.2 ]   |   What function provokes that consequence
            causing_edge = graph.node_in_edges(node.id)[0]
            causing_function = graph.get_node_by_id(causing_edge.from_id)


#       [  3  ]   |   Explore all pvk edges
    while 1:
        in_edge = [edge for edge in graph.node_in_edges(causing_function.id) if "pvk" in edge.name][0]
        in_node = graph.get_node_by_id(in_edge.from_id)
        if in_node.node_type == "actions":
            actions.append(in_edge)
            break
        causing_function = in_node


#       [  4  ]   |   Check the last function found
    if "if_function" in causing_function.node_type:
        goal = causing_function.name
    else:
        break


#       [  5  ]   |   Show plan
acts = [act.name.replace("pvk ","") for act in actions]
print("plan:", acts[::-1])


#       [  6  ]   |   Graph everything
#graph.nodes = graph.organize_in_layers()

#graph_viewer(graph.nodes, graph.edges)