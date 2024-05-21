import bisect
from collections import defaultdict
import nltk

from typing import Optional
from dataclasses import dataclass, field

from prototyping.grass_parser_v2.graph import Edge, Graph, NodeEnergyMap
from prototyping.grass_parser_v2.server import start_server
from src.knowledge_base.hierarchy import DictHierarchy


# nltk.download('conll2000')
# from nltk.corpus import conll2000

# collected = defaultdict(list)
# for tree in conll2000.chunked_sents():
#     for subtree in tree.subtrees():
#         if subtree.label() == 'NP' and subtree.height() == 2:
#             tags = [tag for word, tag in subtree.leaves()]
#             if {'CD', 'NNP', '$', '``'}.intersection(tags):
#                 continue

#             collected['+'.join(tags)].append(subtree.leaves())
# # sentence = conll2000.sents()[1]

# sentence = collected['DT+JJ+NN'][1]

# "on", "the", "construction", "site"]
# breakpoint()

@dataclass
class Pattern:
    concept: str
    nodes: list[str]


# sentence = [
#     "Word_my", "Word_brother", "Word_is", "Word_running",
#     # "Word_my", "Word_brother", "Word_is", "Word_far",
# ]
# sentence = ["i", "saw", "a", "crane", "i", "saw"]
sentence = ["my", "brother", "is", "running"]
sentence = [
    f"Word_{word}" for word in sentence
]

# def _char_to_concept(ch: str):
#     if ch == " ":
#         return "CharacterSpace"

#     return f"Character_{ch}"

# sentence = [
#     _char_to_concept(ch)
#     for ch in "my brother is running"
# ]


"""
solution - lookup with expanded concepts by default
"""

patterns = [
    # Pattern("_IGNORE_", [
    #     "CharacterSpace",
    # ]),
    Pattern("LivingEntityIsDoingProcess", [
        "LivingEntity", "IsDoing", "Process",
    ]),
    Pattern("NonLivingEntityIsDoingProcess", [
        "NonLivingEntity", "IsDoing", "Process",
    ]),
    Pattern("NonLivingEntityIsBeingActivity", [
        "NonLivingEntity", "IsBeing", "Activity",
    ]),
    Pattern("NonLivingEntityIsBeingFar", [
        "NonLivingEntity", "IsBeing", "DistanceFar",
    ]),
    Pattern("LivingEntityIsBeingFar", [
        "LivingEntity", "IsBeing", "DistanceFar",
    ]),
    Pattern("NonLivingEntity", [
        "PossessivePronoun", "Hobby",
    ]),
    Pattern("LivingEntity", [
        "PossessivePronoun", "RelativeBrother",
    ]),
    Pattern("NonLivingEntity", [
        "PossessivePronoun", "Home",
    ]),
    Pattern("ConstructionSite", [
        "Word_construction", "Word_site",
    ]),
    Pattern("EntityDidAction", [
        "LivingEntity", "ActionPast",
    ]),
    Pattern("EntityDidActionWithEntity", [
        "LivingEntity", "ActionPast", "Entity",
    ]),
    Pattern("IndefiniteEntityReference", [
        "IndefiniteArticleA", "Entity",
    ]),
]

word_concepts = {
    "Word_my": ["PossessivePronoun"],
    "Word_hobby": ["Hobby"],
    "Word_brother": ["RelativeBrother"],
    "Word_home": ["Home"],
    "Word_is": ["IsBeing", "IsDoing"],
    "Word_running": ["ProcessRunning", "ActivityRunning"],
    "Word_far": ["DistanceFar"],
    "Word_crane": ["CraneBird", "ConstructionCrane"],
    "Word_i": ["I", ],
    "Word_saw": ["SawPastAction", "SawTool"],
    "Word_a": ["IndefiniteArticleA", ],
    "Word_the": ["DefiniteArticleThe", ],
    "Word_on": ["OnPreposition", ],
}

for _word, _concepts in word_concepts.items():
    for _concept in _concepts:
        patterns.append(Pattern(_concept, [_word, ]))

    # patterns.append(Pattern(_word, [
    #     f"Character_{letter}"
    #     for letter in _word.split("_")[1]
    # ]))


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
    "Process": ["ProcessRunning", ],
    "ActionPast": ["SawPastAction", ],
    "Action": ["ActionPast", ],
    "LivingEntity": ["RelativeBrother", "I", "CraneBird"],
    "Entity": ["LivingEntity", "NonLivingEntity", "IndefiniteEntityReference"],
    "NonLivingEntity": ["ConstructionCrane", ],
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


for pattern in patterns:
    g.sizes[pattern.concept] = len(pattern.nodes) - 1


energy_map = NodeEnergyMap(g)
# g.update_edge(Edge(
#     start="ConstructionSite",
#     end="ConstructionCrane",
#     type_name="associated",
# ), 1.0)


@dataclass
class Match:
    layer_idx: int = field(repr=False)
    size: int = 1
    concept: Optional[str] = None
    children: list["Match"] = field(default_factory=list, repr=False)

    def __repr__(self) -> str:
        return f"Match({self.concept}, {self.size})"
    
    def __gt__(self, other):
        # random order for the ambiguity priority queue
        # we don't care which match is the first one 
        # since they are both equally ambiguous
        return hash(self) > hash(other)


class Tree:
    def __init__(self) -> None:
        self.layers = [[],]
        self.call_stack = []
        self.validation_stack = []
        self.ambiguous_matches_queue = []
        self.tree_locations = []

    def add_word(self, word: str):
        for idx, layer in enumerate(self.layers):
            layer.append(Match(layer_idx=idx))
        match = self.layers[0][-1]
        match.concept = word

    def match(self, idx, size):
        print("Matching", idx, size)

        if idx + size + 1 > len(self.layers[0]):
            breakpoint()
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

            
        for _ in range(2):
            for layer in reversed(self.layers):
                try:
                    match = layer[current_idx]
                except IndexError:
                    break
                if match.concept is None:
                    continue
                concepts.append(match.concept)
                current_idx += match.size
                break

        indices = list(range(len(concepts)))

        res = self._make_lookup(idx, size, concepts, indices)

        if not res:
            if self.tree_locations:
                self.validation_stack.append(self.tree_locations[-1])
            
            print("Can't expand, starting a new tree")
            self.tree_locations.append(idx)
            # if self.call_stack:
            #     breakpoint()
            #     pass
            # assert not self.call_stack
            new_idx = idx + sum([
                match.size
                for match in matches
            ])
            self.call_stack.append((new_idx, 0))
            return
        
        print('found', res[:3])

        pattern_name = res[0][0]
        pattern_nodes = pattern_map[pattern_name].nodes

        if len(pattern_nodes) - 1 < len(matches):
            breakpoint()
            pass

        new_idx = idx
        for match, node in zip(matches, pattern_nodes):
            if node not in hierarchy.get_parents(match.concept):
                print('not equal!!')
                if new_idx == idx:
                    if self.tree_locations:
                        self.validation_stack.append(self.tree_locations[-1])

                    if not self.call_stack:
                        print('Adding new tree location', idx, self.call_stack)
                        self.tree_locations.append(idx)

                    self.call_stack.append((idx + size + 1, 0))
                    # full mismatch
                    return
                # on unsuccessful match go try matching further
                # and then come back
                self.call_stack.append((idx, size))
                self.call_stack.append((new_idx, 0))
                return
            new_idx += match.size

        if len(pattern_nodes) - 1 > len(matches):
            # we are not ready to match this
            new_size = sum([
                match.size
                for match in matches
            ])
            print("Expanding match")
            self.call_stack.append((idx, new_size))
            return
            
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

            if len(res) > 1:
                certanty_level = round(res[0][1] - res[1][1], 2)
                bisect.insort(self.ambiguous_matches_queue, (certanty_level, self.layers[new_layer_idx][idx]))
                self.ambiguous_matches_queue = self.ambiguous_matches_queue[:10]
            
            if self.call_stack:
                print("Sucess, returning back")
                return
            
            # if self.tree_locations:
            #     self.validation_stack.append(self.tree_locations[-1])

            print("Sucess, try expanding up")
            # on successful match go up+forward
            self.call_stack.append((idx, size))
            return
        
    def _make_lookup(self, idx, size, concepts, indices):
        emap = NodeEnergyMap(g)
        words = []

        for word_idx in range(max(idx - 2, 0), min(len(self.layers[0]), idx + size + 1 + 2)):
            word_concept = self.layers[0][word_idx].concept
            emap.add_energy(word_concept, 0.3, propagation={
                "pattern": 0.8,
                "parent": 1.0,
            }, commit=False)
            words.append(word_concept)

            for layer in self.layers[1:]:
                match_concept = layer[word_idx].concept
                if match_concept is None:
                    continue
                emap.add_energy(match_concept, 0.3, propagation={
                    "pattern": 0.8,
                    "parent": 1.0,
                }, commit=False)

        print('concepts', concepts)

        emap.reverse_propagate(propagation=1.0)
        emap.energies[''] = 0

        if concepts == ['Word_a', 'CraneBird', 'EntityDidAction']:
            breakpoint()

        res = g.lookup(
            *concepts,
            indices=indices,
            depth=5,
            depth_decay={
                "pattern": 0.5,
                "parent": 0.0,
            },
            energy_map=emap,
            index_mismatch_penalty=0.5,
            result_edge_types={"pattern", },
            transition_edge_types={"parent", "pattern"},
        )

        # if res[0][0] == 'EtityDidAction':
            # breakpoint()

        return res

    def validate_column(self, idx):
        for layer in self.layers[1: ]:
            match = layer[idx]
            if match.concept is None:
                break
            self._validate_match(idx, match)

    def _validate_match(self, idx, match: Match):
        # TODO: way too much code duplication, fix it
        matches = []
        concepts = []
        indices = []

        current_idx = idx

        while current_idx <= idx + match.size:
            if current_idx == idx:
                found = False
                for layer in reversed(self.layers):
                    _match = layer[current_idx]
                    if found:
                        matches.append(_match)
                        concepts.append(_match.concept)
                        current_idx += _match.size
                        break
                    if match is _match:
                        found = True
                else:
                    raise ValueError("No match found")
                
            for layer in reversed(self.layers):
                _match = layer[current_idx]
                if current_idx == idx and match is not _match:
                    continue
                if _match.concept is None:
                    continue
                matches.append(_match)
                concepts.append(_match.concept)
                current_idx += _match.size
                break
            else:
                raise ValueError("No match found")
    
        for _ in range(2):
            for layer in reversed(self.layers):
                try:
                    _match = layer[current_idx]
                except IndexError:
                    break
                if _match.concept is None:
                    continue
                concepts.append(_match.concept)
                current_idx += _match.size
                break

        indices = list(range(len(concepts)))

        res = self._make_lookup(idx, match.size, concepts, indices)

        if not res:
            breakpoint()

        if res and res[0][0] != match.concept:
            # reset this match and matches above
            # TODO: also reset any matches that use this match in the higher layers
            for layer in reversed(self.layers):
                _match = layer[idx]
                if _match.concept is None:
                    continue
                _match.concept = None
                _match.children.clear()
                if _match is match:
                    break
            
            self.call_stack.append((idx, 0))
    
    def run(self):
        self.call_stack.append((0, 0))
        
        while self.call_stack or self.validation_stack:
            if self.validation_stack:
                idx = self.validation_stack.pop()
                self.validate_column(idx)
            elif self.call_stack:
                idx, size = self.call_stack.pop()
                self.match(idx, size)

    def find_last_match(self, idx):
        last_match = None
        for layer in reversed(self.layers[1:]):
            try:
                match = layer[idx]
            except IndexError:
                return None, None
            
            if match.concept is not None:
                last_match = match
                new_idx, next_match = self.find_last_match(idx + match.size)
                if next_match is not None:
                    return new_idx, next_match
                return idx, last_match
                break

        return None, None


start_server()
tree = Tree()
for word in sentence:
    tree.add_word(word)
tree.run()
# lmi, lm = tree.find_last_match(0)
# assert not tree.call_stack
# print('\n\n\n\n\n\n')
# tree.match(lmi + lm.size, 0, is_end=False)

print("DONE")

breakpoint()
pass