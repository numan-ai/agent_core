import graph_lib, pygame, sys

from math import pi, sin, cos
from uuid import uuid4
from dataclasses import dataclass, field
from saving_loading import *

"""
	CONTROLS

LMB	            Drag
Alt + LMB       Create edge		    [go to terminal]
Shift + LMB	    Create node	        [go to terminal]
Ctrl + LMB	    Delete node/edge

Ctrl + G	    Save		        [go to terminal]
Ctrl + C	    Load		        [go to terminal]

    NAMING STANDARDS

NODES TYPES:

Exact types: object, attribute, actions, consequence

Must contain: function (Normal x = True are called function, conditional middle functions are if_function)

NODES NAME:
actions for actions node
functions: python code like x = True

EDGES TYPES:

with edges their name must be one of these:

pvk (Provokes)
con (Consequence)
att (Attribute)
x, y...   (Function arg)

"""

NODE_RADIUS = 50
WHITE_SPACE = 400

def graph_viewer(graph: graph_lib.Graph, automatic_sort=False):
    edge_creation = 1
    pygame.init()

    f = lambda p1, p2, r: p1 + r * (p2 - p1)

    SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen mode
    WIDTH, HEIGHT = SCREEN.get_size()
    pygame.display.set_caption("Graph Viewer")

    clock = pygame.time.Clock()

    @dataclass
    class Node:
        node_name: str
        node_id: str|int = field(default_factory=lambda:str(uuid4()))
        color: str = "blue"
        letter_color: str = "white"
        radius: int = NODE_RADIUS
        shape: str = "circle"
    
    def draw_node(node):
        if node.shape == "circle":
            pygame.draw.circle(SCREEN, node.color, node.position, node.radius)
        elif node.shape == "square":
            pygame.draw.rect(SCREEN, node.color, (
                node.position[0] - node.right//2,
                node.position[1] - node.bottom//2,
                node.right,
                node.bottom),border_radius = node.border_radius)
        elif node.shape == "triangle":
            pygame.draw.polygon(SCREEN, node.color, (
                (node.position[0] + node.c1[0], node.position[1] + node.c1[1]),
                (node.position[0] + node.c2[0], node.position[1] + node.c2[1]),
                (node.position[0] + node.c3[0], node.position[1] + node.c3[1])))
        font = pygame.font.SysFont(None, 20)
        text = font.render(node.node_name, True, node.letter_color)
        text_rect = text.get_rect(center=node.position)
        SCREEN.blit(text, text_rect)

    def show(text, x, y):
        font = pygame.font.SysFont(None, 20)
        text = font.render(text, True, "black")
        text_rect = text.get_rect(center=(x, y))
        SCREEN.blit(text, text_rect)

    def is_inside_circle(x, y, circle_x, circle_y, radius):
        return (x - circle_x) ** 2 + (y - circle_y) ** 2 <= radius ** 2
    
    def is_inside_square(x, y, square_left, square_right, square_top, square_bottom):
        return (square_left < x < square_right) and (square_top < y < square_bottom)

    def is_inside_triangle(x, y, c1, c2, pos):
        c1 = (c1[0] + pos[0], c1[1] + pos[1])
        c2 = (c2[0] + pos[0], c2[1] + pos[1])
        l1 = lambda lx: -(3)**(1/2) * (lx - c1[0]) + c1[1]
        l2 = lambda lx: (3)**(1/2) * (lx - c1[0]) + c1[1]
        return (l1(x) < y) and (l2(x) < y) and (c2[1] > y)

    def style_node(node, affected_node):
        if node.node_type == "object":
            affected_node.color = (255, 49, 49)
        if "function" in node.node_type:
            affected_node.color = "black"
            affected_node.color = "white"
            affected_node.letter_color = "black"
            affected_node.shape = "square"
            affected_node.right = 130
            affected_node.bottom = 50
            affected_node.border_radius = 0
        if node.node_type == "attribute":
            affected_node.radius = 35
            affected_node.color = (115, 115, 115)
        if node.node_type == "actions":
            affected_node.radius = 70
            affected_node.color = (255, 145, 77)
            affected_node.c1 = (0,
                        - affected_node.radius)
            affected_node.c2 = (cos(pi/6) * affected_node.radius,
                        - sin(-pi/6) * affected_node.radius)
            affected_node.c3 = (- cos(pi/6) * affected_node.radius,
                        - sin(-pi/6) * affected_node.radius)
            affected_node.shape = "triangle"
        if node.node_type == "consequence":
            affected_node.color = (0, 151, 178)
            affected_node.shape = "square"
            affected_node.right = 130
            affected_node.bottom = 50
            affected_node.border_radius = 15
        if node.node_type == "gate":
            affected_node.color = (0, 0, 130)
            affected_node.shape = "square"
            affected_node.right = 50
            affected_node.bottom = 50
            affected_node.border_radius = 0

    def position_nodes():
        new_nodes = graph.organize_in_layers()
        NODE_SPACING_Y = HEIGHT / (len(new_nodes) + 1)
        WIDTH_2 = WIDTH - WHITE_SPACE
        x_offset = (WIDTH - WIDTH_2) / 2
        for y, row in enumerate(new_nodes):
            for x, node in enumerate(row):
                if len(row) - 1 != 0:
                    x_2 = [n * WIDTH_2 / (len(row) - 1) for n in range(len(row) + 1)][x]
                else:
                    x_2 = WIDTH_2 / 2
                node.position = (x_2 + x_offset, (y + 1) * NODE_SPACING_Y)
        output = []
        for row in new_nodes:
            output += row
        return output

    def hitbox_click(pos, input_node):
        condition = False
        if input_node.shape == "circle":
            if is_inside_circle(pos[0], pos[1], input_node.position[0], input_node.position[1],
                                NODE_RADIUS):
                condition = True
        elif input_node.shape == "square":
            if is_inside_square(pos[0], pos[1],
                                input_node.position[0] - input_node.right//2,
                                input_node.position[0] + input_node.right//2,
                                input_node.position[1] - input_node.bottom//2,
                                input_node.position[1] + input_node.bottom//2
                                ):
                condition = True
        else:
            if is_inside_triangle(pos[0], pos[1], input_node.c1, input_node.c2, input_node.position):
                condition = True
        return condition

    def close_to_edge(x1, y1, x2, y2, x3, y3):
        if x1 < x3 < x2 or x2 < x3 < x1 and y1 < y3 < y2 or y2 < y3 <y1:
            m1 = (y2-y1)/(x2-x1)
            m2 = -(x2-x1)/(y2-y1)
            xh = (m1*x1 - m2*x3 - y1 + y3) / (m1 - m2)
            yh = m1 * (xh - x1) + y1
            if ((x3-xh)**2 + (y3-yh)**2)**(1/2) < 10:
                return True

    def initialize():
        global Nodes
        Nodes = []
        if automatic_sort:
            initial_nodes = position_nodes()
        else:
            initial_nodes = ([node for node in graph.nodes if "position" in vars(node).keys()] or position_nodes())
        for node in initial_nodes:
            new_node = Node(node.name, node.id)
            new_node.position = node.position
            new_node.node_type = node.node_type
            new_node.value = node.value
            style_node(node, new_node)
            Nodes.append(new_node)

    def decir(texto, action):
        texto = texto.split(": ")[1]
        if action == "save":
            path = texto
            if path:
                for node in Nodes:
                    graph.get_node_by_id(node.node_id).position = node.position
                if ".json" not in path:
                    path += ".json"
                save(graph, "LRDS/"+path)
        if action == "load":
            path = texto
            if path:
                if ".json" not in path:
                    path += ".json"
                graph.nodes, graph.edges = load("LRDS/"+path)
                initialize()
        if action == "new_node":
            if "|" in texto:
                node_name, node_type = texto.split("|")
                if node_type in ["att","obj","act","func","ifunc","con"]:
                    node_type = {"att":"attribute",
                                 "obj":"object",
                                 "act":"actions",
                                 "func":"function",
                                 "ifunc":"if_function",
                                 "con":"consequence"}[node_type]
                common_id = str(uuid4())
                new_node = Node(node_name, common_id)
                new_node.node_type = node_type
                new_node.position = pygame.mouse.get_pos()
                graph.nodes.append(graph_lib.Node(node_name, node_type, position = new_node.position, id=common_id))
                style_node(new_node, new_node)
                Nodes.append(new_node)
            else:
                print(f"Node '{texto}' couldn't be created")
        if action == "new_edge":
            edge_name = texto
            graph.edges.append(graph_lib.Edge(unnecessary_object.start_id, unnecessary_object.end_id, edge_name))

        #if action == "new_edge":
    class TextEntry:
        def __init__(self):
            self.rect = pygame.Rect(200,650,950,50)
            self.string = ""
            self.render()
            self.lock = 1
            self.last_action = ""
        def write(self, key):
            if self.lock == 0:
                if key != 13:
                    if key == 8:self.string = self.string[:-1]
                    else:
                        try: self.string += chr(key)
                        except ValueError:pass
            if key == 13 or isinstance(key, str):
                if self.lock == 0:
                    self.lock = 1
                    decir(self.string, self.last_action)
                elif key != 13:
                    self.lock = 0
                    self.string = key
            self.render()
        def erase(self):
            self.string = self.string[:-1]
        def show(self):
            pygame.draw.rect(SCREEN, "black", self.rect)
            SCREEN.blit(self.text, self.rect.topleft)
        def render(self):
            font2 = pygame.font.SysFont(None, 40)
            self.text = font2.render(self.string, True, "white")

    @dataclass
    class UnnecessaryClass:
        start_id = 0
        end_id = 0

    unnecessary_object = UnnecessaryClass()
    dragging = False
    selected_node = None
    textentry = TextEntry()

    initialize()
    while True:
        SCREEN.fill("black")
        pressed_keys = pygame.key.get_pressed()
        ctrl_pressed = pressed_keys[pygame.K_LCTRL]
        shift_pressed = pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]
        alt_pressed = pressed_keys[pygame.K_LALT]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not shift_pressed:
                    textentry.write(event.key)
                else:
                    special_keys = {
                        32 : 32,
                        45 : 95,
                        46 : 58,
                        48 : 61,
                        49 : 33,
                        50 : 34,
                        51 : 35,
                        52 : 36,
                        53 : 37,
                        54 : 38,
                        55 : 47,
                        56 : 40,
                        57 : 41}
                    if event.key in special_keys.keys():
                        textentry.write(special_keys[event.key])
                    if 96 < event.key < 123:
                        textentry.write(event.key-32)
                if event.key == pygame.K_g and ctrl_pressed:
                    textentry.last_action = "save"
                    textentry.write("Save to: ")
                if event.key == pygame.K_c and ctrl_pressed:
                    textentry.last_action = "load"
                    textentry.write("Load from: ")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ctrl_pressed:  # Delete
                    if event.button == 1:  # Left mouse button
                        nodes = []
                        for node in Nodes:
                            nodes.append(node.node_id)
                        for node in Nodes:
                            if hitbox_click(event.pos, node):
                                Nodes.remove(node)
                                graph.nodes.remove(graph.get_node_by_id(node.node_id))
                                
                                
                                deletes = graph.node_out_edges(node.node_id) + graph.node_in_edges(node.node_id)

                                for delete in deletes:
                                    graph.edges.remove(delete)

                        for edge in graph.edges:
                            nodes = []
                            for node in Nodes:
                                nodes.append(node.node_id)
                            x1, y1 = graph.get_node_by_id(edge.to_id).position
                            x2, y2 = graph.get_node_by_id(edge.from_id).position
                            if close_to_edge(x1, y1, x2, y2, event.pos[0], event.pos[1]):
                                graph.edges.remove(edge)
                elif shift_pressed:  # Create
                    textentry.last_action = "new_node"
                    textentry.write("name|type: ")
                elif alt_pressed:  # Connect
                    for node in Nodes:
                        if hitbox_click(event.pos, node):
                            if edge_creation == 1:
                                unnecessary_object.start_id = node.node_id
                            else:
                                unnecessary_object.end_id = node.node_id
                                textentry.last_action = "new_edge"
                                textentry.write("name: ")

                            edge_creation *= -1
                    #show(str(edge_creation), 10, 10)
                else:  # Grab
                    if event.button == 1:  # Left mouse button
                        for node in Nodes:
                            if node.shape == "circle":
                                if is_inside_circle(event.pos[0], event.pos[1], node.position[0], node.position[1],
                                                    NODE_RADIUS):
                                    selected_node = node
                                    dragging = True
                                    break
                            elif node.shape == "square":
                                if is_inside_square(event.pos[0], event.pos[1],
                                                    node.position[0] - node.right//2,
                                                    node.position[0] + node.right//2,
                                                    node.position[1] - node.bottom//2,
                                                    node.position[1] + node.bottom//2
                                                    ):
                                    selected_node = node
                                    dragging = True
                                    break
                            else:
                                if is_inside_triangle(event.pos[0], event.pos[1], node.c1, node.c2, node.position):
                                    selected_node = node
                                    dragging = True
                                    break
            elif event.type == pygame.MOUSEBUTTONUP:  # Release
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:  # Drag
                if dragging and selected_node:
                    selected_node.position = (selected_node.position[0] + event.rel[0],
                                              selected_node.position[1] + event.rel[1])

        # Draw edges
        for edge in graph.edges:
            from_node = next((node for node in Nodes if node.node_id == edge.from_id), None)
            to_node = next((node for node in Nodes if node.node_id == edge.to_id), None)
            if from_node is not None and to_node is not None:
                color = (253, 199, 62)
                if "pvk" in edge.name:
                    color = (255, 145, 77)
                if "con" in edge.name:
                    color = (0, 151, 178)
                if "att" in edge.name:
                    color = (115, 115, 115)
                if edge.name == "in" or edge.name == "out":
                    color = (0, 0, 0)
                # Calculate midpoint of the edge
                midpoint = (f(from_node.position[0], to_node.position[0], 0.5), f(from_node.position[1], to_node.position[1], 0.5))
                dir_indicator = (f(from_node.position[0], to_node.position[0], 0.6), f(from_node.position[1], to_node.position[1], 0.6))
                pygame.draw.circle(SCREEN, color, dir_indicator, 8, 2)
                pygame.draw.line(SCREEN, color, from_node.position, to_node.position, 2)
                font = pygame.font.SysFont(None, 20)
                text = font.render(edge.name, True, color)
                text_rect = text.get_rect(center=midpoint)
                SCREEN.blit(text, text_rect)
            else:
                print("Error: Node not found for edge:", edge)

        # Draw nodes
        for node in Nodes:
            draw_node(node)

        if textentry.lock == 0:
            textentry.show()
        pygame.display.flip()
        clock.tick(30)

    
if __name__ == "__main__":
    import graph_lib
    from saving_loading import *

    #nodes, edges = load("testing3.json")
    nodes, edges = [], []

    graph = Graph(nodes, edges)
    graph_viewer(graph)

"""
quita row y tal de nodes [V]
si puedes simplifica a solo usar la base de deatos como haces con edges [V]
input texto [V] ~
refactorizar [V]
	quita médotos de graficación de los nodos [V]
    fíjate en si hacer lo de los nodos como parte de la graficación [V]
    haz más cosas así
guardar y abrir [V]

Don't:
- Do weird things like pressing alt + LMB and while entering data pressing it again. That's crazy
- Erase the text from the data entering

Add camera movement
Add extra data from hovering
Add value setting or extra data setting like above ^^
Add consequence autocompletion
Add visual function and consequence autocompletion activated or not
"""