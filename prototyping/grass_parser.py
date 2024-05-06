from dataclasses import dataclass
from typing import Hashable
from grass import AssociativeEnergyGraph

words = open('./prototyping/10000_words.txt', 'r').read().split('\n')

gf = AssociativeEnergyGraph([
    (letter, word, 1.0)
    for word in words
    for letter in word
], bidirectional=False)


@dataclass
class HyperEdge:
    nodes: list[Hashable]
    index: int = 0
    energy: float = 1.0
    mismatch: float = 0.1

    def get_score(self):
        return self.energy - self.mismatch - (len(self.nodes) - self.index) * 0.2


hypergraphs = [
    HyperEdge(list(word))
    for word in words
]

"this is understanable"
["Word_this", "Word_is", "Word_understand", "Suffix_able"]
["Word_this", "Word_is", "Word_understandable"]

word = 'heis'# friends'
for letter in word:
    for edge in hypergraphs:
        try:
            edge_node = edge.nodes[edge.index]
        except IndexError:
            edge.energy *= 0.6
            continue

        if edge_node == letter:
            edge.energy += 0.2
            edge.index += 1
        else:
            edge.mismatch *= 1.5
            # try next edge node
            try:
                edge_node = edge.nodes[edge.index + 1]
            except IndexError:
                edge.energy *= 0.6
                continue
            if edge_node == letter:
                edge.energy += 0.2
                edge.index += 2
            else:
                edge.energy *= 0.6
        
        edge.energy = min(edge.energy, 1.0)

    hypergraphs.sort(key=lambda x: x.get_score(), reverse=True)

    # gf.add_energy(letter, 1, 0.5)

# print(gf.lookup(*list(word)))
breakpoint()
pass
