import nltk

from typing import Optional
from dataclasses import dataclass, field

from prototyping.grass_parser_v2.graph import Edge, Graph, NodeEnergyMap
from src.knowledge_base.hierarchy import DictHierarchy


nltk.download('conll2002')

breakpoint()


@dataclass
class Pattern:
    concept: str
    nodes: list[str]


sentence = [
    "Word_my", "Word_brother", "Word_is", "Word_running",
    # "Word_my", "Word_brother", "Word_is", "Word_far",
]

patterns = [
    Pattern("LivingEntityIsDoingProcess", [
        "LivingEntity", "IsDoing", "Process"
    ]),
    Pattern("NonLivingEntityIsDoingProcess", [
        "NonLivingEntity", "IsDoing", "Process"
    ]),
    Pattern("NonLivingEntityIsBeingActivity", [
        "NonLivingEntity", "IsBeing", "Activity"
    ]),
    Pattern("NonLivingEntityIsBeingFar", [
        "NonLivingEntity", "IsBeing", "DistanceFar"
    ]),
    Pattern("LivingEntityIsBeingFar", [
        "LivingEntity", "IsBeing", "DistanceFar"
    ]),
    Pattern("NonLivingEntity", [
        "PossessivePronoun", "Hobby"
    ]),
    Pattern("LivingEntity", [
        "PossessivePronoun", "RelativeBrother"
    ]),
    Pattern("NonLivingEntity", [
        "PossessivePronoun", "Home"
    ]),
    # Pattern("P1", ["A", "B", "C"]),
    # Pattern("P2", ["C", "A", "B"]),
]

word_concepts = {
    "Word_my": ["PossessivePronoun"],
    "Word_hobby": ["Hobby"],
    "Word_brother": ["RelativeBrother"],
    "Word_home": ["Home"],
    "Word_is": ["IsBeing", "IsDoing"],
    "Word_running": ["Activity", "Process"],
    "Word_far": ["DistanceFar"],
}

for _word, _concepts in word_concepts.items():
    for _concept in _concepts:
        patterns.append(Pattern(_concept, [_word, ]))



for pattern in patterns:
    # add tails to patterns
    # empty string represents the end of the pattern
    pattern.nodes.append("")

pattern_map = {
    pattern.concept: pattern
    for pattern in patterns
}

hierarchy = DictHierarchy(children={
    "Activity": ["ActivityRunning"],
    "Process": ["ProcessRunning"],
    "LivingEntity": ["RelativeBrother", ],
    # "A": ["A1"],
    # "B": ["B1"],
    # "C": ["C1"],
    # "C1": ["C2"],
})

g = Graph([
    Edge(node, pattern.concept, "pattern", i)
    for pattern in patterns
    for i, node in enumerate(pattern.nodes)
] + [
    Edge(child, parent, "parent", -1)
    for parent, children in hierarchy.children.items()
    for child in children
])

energy_map = NodeEnergyMap(g)
energy_map.add_energy("P2", 1.0)


@dataclass
class Match:
    layer_idx: int = field(repr=False)
    size: int = 1
    concept: Optional[str] = None
    children: list["Match"] = field(default_factory=list, repr=False)


class Tree:
    def __init__(self) -> None:
        self.layers = [[], [], [], []]
        self.call_stack = []

    def add_word(self, word: str):
        for idx, layer in enumerate(self.layers):
            layer.append(Match(layer_idx=idx))
        match = self.layers[0][-1]
        match.concept = word

    def match(self, idx, size, is_end: bool = False):
        print("Matching", idx, size, "end" if is_end else "")

        if idx + size + 1 > len(self.layers[0]):
            return

        matches = []
        concepts = []
        indices = []

        current_idx = idx

        while current_idx <= idx + size:
            for layer in reversed(self.layers):
                match = layer[current_idx]
                if match.concept is None:
                    continue
                matches.append(match)
                concepts.append(match.concept)
                current_idx += match.size
                break

        if is_end:
            concepts.append("")

        indices = list(range(len(concepts)))

        emap = NodeEnergyMap(g)
        words = []

        for word_idx in range(max(idx - 2, 0), min(len(self.layers[0]), idx + size + 1 + 2)):
            word_concept = self.layers[0][word_idx].concept
            emap.add_energy(word_concept, 0.3, propagation=0.9, commit=False)
            words.append(word_concept)

            for layer in self.layers[1:]:
                match_concept = layer[word_idx].concept
                if match_concept is None:
                    continue
                emap.add_energy(match_concept, 0.2, propagation=0.9, commit=False)
        
        # for word_idx in range(idx + size + 1, min(len(self.layers[0]), idx + size + 1 + 2)):
        #     word_concept = self.layers[0][word_idx].concept
        #     emap.add_energy(word_concept, 0.3, propagation=0.9, commit=False)
        #     words.append(word_concept)
        # emap._NodeEnergyMap__energy_uncommitted
        print('concepts', concepts)
        emap.reverse_propagate(propagation=1.0)
        emap.energies[''] = 0

        res = g.lookup(
            *concepts,
            indices=indices,
            depth=5,
            depth_decay=0.5,
            energy_map=emap,
            index_mismatch_penalty=0.5,
            result_edge_types={"pattern", },
            transition_edge_types={"parent", "pattern"},
        )

        if not res:
            return

        print('found', res[:3])

        pattern_name = res[0][0]
        pattern_nodes = pattern_map[pattern_name].nodes

        if len(pattern_nodes) - 1 < len(matches):
            breakpoint()
            pass

        new_idx = idx
        for match, node in zip(matches, pattern_nodes):
            if match.concept != node:
                print('not equal!!')
                # on unsuccessful match go try matching further
                # and then come back
                # new_idx = idx + matches[0].size
                self.call_stack.append((idx, size))
                return self.match(new_idx, 0, is_end=False)
            new_idx += match.size

        if len(pattern_nodes) - 1 > len(matches):
            # we are not ready to match this
            new_size = sum([
                match.size
                for match in matches
            ])
            print("Expanding match")
            return self.match(idx, new_size)
            
        new_layer_idx = max([
            match.layer_idx
            for match in matches
        ]) + 1

        if len(matches) == len(pattern_nodes) - 1:
            if new_layer_idx >= len(self.layers):
                self.layers.append([
                    Match(layer_idx=new_layer_idx)
                    for _ in range(len(self.layers[0]))
                ])
            
            self.layers[new_layer_idx][idx].concept = pattern_name
            self.layers[new_layer_idx][idx].children = matches
            self.layers[new_layer_idx][idx].size = sum([
                match.size
                for match in matches
            ])
            if self.call_stack:
                print("Sucess, returning back")
                new_idx, new_size = self.call_stack.pop()
                return self.match(new_idx, new_size, is_end=False)

            print("Sucess, try expanding up")
            # on successful match go up+forward
            return self.match(idx, size, is_end=False)


tree = Tree()
tree.add_word(sentence[0])
tree.add_word(sentence[1])
tree.add_word(sentence[2])
tree.add_word(sentence[3])
tree.match(0, 0, is_end=False)

breakpoint()
pass