import random
import time
from uuid import uuid4
from prototyping.grass_parser_v2.graph import Edge, Graph, NodeEnergyMap


nodes_num = 1000
edges_num = 50000

nodes = [
    str(uuid4())
    for _ in range(nodes_num)
]

g = Graph([
    Edge(random.choice(nodes), random.choice(nodes), "parent", random.randint(0, 3))
    for _ in range(edges_num)
])

emap = NodeEnergyMap(g)
print('start')

forward_time = 0
backward_time = 0
count = 100

for i in range(count):
    print(f"{i + 1} / {count}", end='\r')
    t1 = time.perf_counter_ns()
    for _ in range(4):
        emap.add_energy(random.choice(nodes), 1.0, propagation={
            "parent": 0.8
        }, commit=False)

    t2 = time.perf_counter_ns()

    emap.reverse_propagate(propagation=0.7)
    t3 = time.perf_counter_ns()

    forward_time += t2 - t1
    backward_time += t3 - t2
print()
print('forward', int(forward_time / edges_num / count))
print('backward', int(backward_time / edges_num / count))
# g.lookup(
#     *[random.choice(nodes) for _ in range(5)]
# )
