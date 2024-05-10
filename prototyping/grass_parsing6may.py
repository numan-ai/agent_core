from dataclasses import dataclass
import math
import random
import time
from typing import Hashable
from grass import AssociativeEnergyGraph

from src.knowledge_base.hierarchy import DictHierarchy

# we can't find all concepts of any word.
# because any word has a concept of "LiteralWord", which will make the parsing so much slower.
# or we can..


"""
PROBLEMS FOR PARSING:
+ linear-time parsing
+ words can be ambiguous and their meaning depends on different things (list them)
+ structure around conjunctions is ambiguous
+ statements can have no separation between them
- incorrect tense can be used for (I did looked), but people still understand this. same for other word forms
- sentences can have unknown words, but the structure can still be understood

Ambiguity influence types:
+ running (previous words trigger the correct pattern). Done with the local context energies.
+ and/light (next words trigger the correct pattern). When we fail to continue building the pattern we update the energies with the new words and concepts and try again.
- crane (local context? influences associations). We build WM representation of the sentence and once we see that the context was wrong we rebuild it, reevaluating the meaning of the sentence
+ apple (general context?, mentioned words before influece associations). Solved by adding another layer of energies for the global context.
"""


sentence = ["Word_my", "Word_brother", "Word_is", "Word_running", ]

aeg = AssociativeEnergyGraph([
    ("Word_my", "PossessivePronoun", 1.0),
    ("Word_hobby", "Hobby", 1.0),
    ("Word_brother", "RelativeBrother", 1.0),
    ("Word_is", "IsBeing", 1.0),
    ("Word_is", "IsDoing", 1.0),
    ("Word_running", "Activity", 1.0),
    ("Word_running", "Process", 1.0),

    # ("PossessivePronoun", "NonLivingEntity", 1.0),
    # ("PossessivePronoun", "LivingEntity", 1.0),
    # ("Hobby", "NonLivingEntity", 1.0),
    # ("RelativeBrother", "LivingEntity", 1.0),

    # ('NonLivingEntity', 'NonLivingEntityIsDoingActivity', 1.0),
    # ('LivingEntity', 'LivingEntityIsDoingActivity', 1.0),
    # ('IsDoing', 'LivingEntityIsDoingActivity', 1.0),
    # ('Activity', 'LivingEntityIsDoingActivity', 1.0),
], bidirectional=False)

global_level = aeg.add_energy_layer("global")
local_level = aeg.add_energy_layer("local")

patterns = {
    "LivingEntityIsDoingActivity": ["LivingEntity", "IsDoing", "Activity"],
    "NonLivingEntityIsDoingActivity": ["NonLivingEntity", "IsDoing", "Activity"],
    "NonLivingEntity": ["PossessivePronoun", "Hobby"],
    "LivingEntity": ["PossessivePronoun", "RelativeBrother"],
}

for pattern_concept, pattern_nodes in patterns.items():
    for pattern_node in pattern_nodes:
        aeg.set_weight(pattern_node, pattern_concept, 1.0)


# hierarchy = DictHierarchy(children={
#     "Activity": ["ActivityRunning"],
#     "Process": ["ProcessRunning"],
#     "LivingEntity": ["RelativeBrother", ],
# })

pattern_name = None
pattern_nodes = None
pattern_idx = 0

for word_idx in range(len(sentence)):
    local_level.add_energy(sentence[word_idx], energy=1.0, propagation=1.0)
    if word_idx < len(sentence) - 1:
        # look ahead
        local_level.add_energy(sentence[word_idx + 1], energy=1.0, propagation=1.0)

    concept = aeg.lookup(sentence[word_idx])[0][0]
    if pattern_nodes is None:
        pattern_concept = aeg.lookup(concept)[0][0]
        pattern_name = pattern_concept
        pattern_nodes = patterns[pattern_concept]

        for pattern_node in pattern_nodes[1:]:
            local_level.add_energy(pattern_node, energy=1.0, propagation=1.0)
    else:
        node_concept = pattern_nodes[pattern_idx]
        if node_concept != concept:
            # match failed, try another option
            raise NotImplementedError("Pattern node does not match concept")

    pattern_idx += 1

    if len(pattern_nodes) == pattern_idx:
        print("Pattern matched", pattern_name)
        if word_idx == len(sentence) - 1:
            break
        # find new pattern
        pattern_concept = aeg.lookup(pattern_name)[0][0]
        pattern_name = pattern_concept
        pattern_nodes = patterns[pattern_concept]

        pattern_idx = 1

        for pattern_node in pattern_nodes[1:]:
            local_level.add_energy(pattern_node, energy=1.0, propagation=1.0)

if len(pattern_nodes) != pattern_idx:
    print("Pattern NOT matched", pattern_name)
    print(pattern_nodes[pattern_idx:])

breakpoint()
pass
