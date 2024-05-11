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


sentence = [
    "Word_my", "Word_brother", "Word_is", "Word_running", 
    "Word_my", "Word_brother", "Word_is", "Word_far",
]

patterns = {
    "LivingEntityIsDoingActivity": ["LivingEntity", "IsDoing", "Activity"],
    "NonLivingEntityIsDoingActivity": ["NonLivingEntity", "IsDoing", "Activity"],
    "NonLivingEntityIsBeingFar": ["NonLivingEntity", "IsBeing", "DistanceFar"],
    "LivingEntityIsBeingFar": ["LivingEntity", "IsBeing", "DistanceFar"],
    "NonLivingEntity": ["PossessivePronoun", "Hobby"],
    "LivingEntity": ["PossessivePronoun", "RelativeBrother"],
    "NonLivingEntity": ["PossessivePronoun", "Home"],
}

word_concepts = {
    "Word_my": ["PossessivePronoun"],
    "Word_hobby": ["Hobby"],
    "Word_brother": ["RelativeBrother"],
    "Word_home": ["Home"],
    "Word_is": ["IsBeing", "IsDoing"],
    "Word_running": ["Activity", "Process"],
    "Word_far": ["DistanceFar"],
}

hierarchy = DictHierarchy(children={
    "Activity": ["ActivityRunning"],
    "Process": ["ProcessRunning"],
    "LivingEntity": ["RelativeBrother", ],
})

aeg = AssociativeEnergyGraph([

], bidirectional=False)

global_level = aeg.add_energy_layer("global")
local_level = aeg.add_energy_layer("local")

for word, concepts in word_concepts.items():
    for concept in concepts:
        aeg.set_weight(word, concept, 1.0)

for pattern_concept, pattern_nodes in patterns.items():
    for pattern_node in pattern_nodes:
        aeg.set_weight(pattern_node, pattern_concept, 1.0)

pattern_concept = None
pattern_nodes = None
pattern_idx = 0

collected_words = []

for word_idx in range(len(sentence)):
    local_level.add_energy(sentence[word_idx], energy=1.0, propagation=1.0)
    if word_idx < len(sentence) - 1:
        # look ahead
        local_level.add_energy(sentence[word_idx + 1], energy=1.0, propagation=1.0)

    concept = aeg.lookup(sentence[word_idx])[0][0]
    collected_words.append(sentence[word_idx])

    if pattern_nodes is None:
        pattern_concept = aeg.lookup(concept)[0][0]
        pattern_nodes = patterns[pattern_concept]

        print("Matching:", pattern_concept, pattern_nodes)

        for pattern_node in pattern_nodes[1:]:
            local_level.add_energy(pattern_node, energy=1.0, propagation=1.0)
    else:
        pattern_concept = aeg.lookup(concept)[0][0]
        pattern_nodes = patterns[pattern_concept]

        assert len(pattern_nodes) >= len(collected_words)

        # check that the pattern matches collected nodes
        for node_idx in range(len(collected_words)):
            breakpoint()
            if pattern_nodes[node_idx] != collected_nodes[node_idx]:
                # match failed, try another option
                raise NotImplementedError("Pattern node does not match concept")

    pattern_idx += 1

    if len(pattern_nodes) == pattern_idx:
        print("Pattern matched")
        aeg.reset_energies(layer_name="local")
        collected_words.clear()

        if word_idx == len(sentence) - 1:
            break
        pattern_concepts = aeg.lookup(pattern_concept)
        
        if len(pattern_concepts) == 0:
            print("No more bigger patterns found")
            # looking for the next pattern
            pattern_concept = None
            pattern_nodes = None
            pattern_idx = 0
        else:
            collected_words.append(None)
            pattern_concept = pattern_concepts[0][0]
            pattern_nodes = patterns[pattern_concept]
            print("Matching:", pattern_concept, pattern_nodes)

            pattern_idx = 1

            for pattern_node in pattern_nodes[1:]:
                local_level.add_energy(pattern_node, energy=1.0, propagation=1.0)

if len(pattern_nodes) != pattern_idx:
    print("Pattern NOT matched", pattern_name)
    print(pattern_nodes[pattern_idx:])

breakpoint()
pass
