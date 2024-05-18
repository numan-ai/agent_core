import random
import time
from uuid import uuid4
from prototyping.grass_parser_v2.graph import Edge, Graph, NodeEnergyMap


nodes_num = 1000
edges_num = 10000

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
t1 = time.perf_counter_ns()
for _ in range(4):
    emap.add_energy(random.choice(nodes), 1.0, propagation=0.8, commit=False)

t2 = time.perf_counter_ns()

emap.reverse_propagate(propagation=0.7)
t3 = time.perf_counter_ns()

print(edges_num)
print('forward', (t2 - t1) / edges_num)
print('backward', (t3 - t2) / edges_num)
# g.lookup(
#     *[random.choice(nodes) for _ in range(5)]
# )
