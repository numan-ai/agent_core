import json
from graph_lib import Graph, Node, Edge

def save(input_graph: Graph, path):
    graph_data = {
        "nodes": [node.__dict__ for node in input_graph.nodes],
        "edges": [edge.__dict__ for edge in input_graph.edges]
    }
    with open(path, 'w') as f:
        json.dump(graph_data, f, indent=4)

def load(path):
    with open(path, 'r') as f:
        loaded_graph_data = json.load(f)
    out_nodes = [Node(**node_data) for node_data in loaded_graph_data["nodes"]]
    out_edges = [Edge(**edge_data) for edge_data in loaded_graph_data["edges"]]
    return (out_nodes, out_edges)

if __name__ == "__main__":
    import pprint

    # Nodes
    nodes = [
        Node("m_e", "object", 0),
        Node("dressed", "attribute", 1),
        Node("out", "attribute", 2),

        Node("x = True", "function", 3),
        Node("x = True", "function", 4),
        Node("x = False", "function", 5),
        Node("x = False", "function", 6),

        Node("x == True", "if_function", 7),

        Node("x == True", "consequence", 8),
        Node("x == True", "consequence", 9),
        Node("x == False", "consequence", 10),
        Node("x == False", "consequence", 11),

        Node("actions", "actions", 12)
    ]

    nodes[1].value = False
    nodes[2].value = False

    # Edges
    edges = [
        Edge(0, 1, "att", 0), Edge(0, 2, "att", 1),
        Edge(1, 3, "x", 2), Edge(1, 5, "x", 3),
        Edge(2, 4, "x", 4), Edge(2, 6, "x", 5),

        Edge(1, 7, "x", 6), Edge(7, 4, "pvk", 7),

        Edge(3, 8, "con", 8), Edge(4, 9, "con", 9),
        Edge(5, 10, "con", 10), Edge(6, 11, "con", 11),

        Edge(12, 3, "pvk dress", 12), Edge(12, 5, "pvk undress", 13),
        Edge(12, 6, "pvk go in", 14), Edge(12, 7, "pvk go out", 15)
    ]

    graph = Graph(nodes, edges)
    save(graph, 'graph_data.json')
    nodes2, edges2 = load('graph_data.json')

    pprint.pprint(nodes2)
    pprint.pprint(edges2)