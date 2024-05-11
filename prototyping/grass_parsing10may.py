import uuid
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

global_level = aeg.get_energy_layer("global")
local_level = aeg.get_energy_layer("local")

for word, concepts in word_concepts.items():
    for concept in concepts:
        patterns[concept] = [word, ]

for pattern_concept, pattern_nodes in patterns.items():
    for pattern_node in pattern_nodes:
        aeg.set_weight(pattern_node, pattern_concept, 1.0)
        # aeg.set_weight(pattern_concept, pattern_node, 1.0)


class Match:
    def __init__(self, aeg) -> None:
        self.concepts = []
        self.child_matches = []
        self.aeg = aeg
        self.energy_layer_name = str(uuid.uuid4())
        self.energy_layer = aeg.get_energy_layer(self.energy_layer_name)
        self.is_finished = False
        self.is_failed = False
        self.pattern_name = None
        self.size = 0

    def reset(self):
        self.concepts.clear()
        self.child_matches.clear()
        self.energy_layer.energy.clear()
        self.size = 0
        self.is_finished = False
        self.is_failed = False
        self.pattern_name = None

    def check_stability(self, layers):
        pattern_name = self.aeg.lookup(
            *self.concepts,
            layer_names=layers
        )[0][0]

        return pattern_name == self.pattern_name

    def add_concept(self, concept, match, layers):
        self.concepts.append(concept)
        self.child_matches.append(match)
        self.energy_layer.add_energy(concept, 1.0, 0.75)

        for layer_name in layers:
            if self.energy_layer_name == layer_name:
                continue
            self.aeg.add_energy(concept, 0.5, 0.75, layer_name=layer_name)

        try:
            pattern_name = self.aeg.lookup(
                *self.concepts,
                layer_names=layers
            )[0][0]
        except IndexError:
            self.is_failed = True

        pattern_nodes = patterns[pattern_name]

        for i, concept in enumerate(self.concepts):
            if concept != pattern_nodes[i]:
                self.is_failed = True
                return
        
        if len(pattern_nodes) != len(self.concepts):
            return
        
        self.is_finished = True
        self.pattern_name = pattern_name


class MatchTree:
    def __init__(self, concepts, aeg) -> None:
        self.concepts = concepts
        self.match_layers = [
            [Match(aeg) for _ in range(len(concepts))]
            for _ in range(5)
        ]
        self.aeg = aeg

    def process(self, x, y, idx = 0, call_stack = None):    
        if call_stack is None:
            call_stack = []

        layers = [
            match_layer[x + idx].energy_layer_name
            for match_layer in self.match_layers
        ]

        match: Match = self.match_layers[y][x]

        # check stability of all sub matches
        for sub_idx in range(0, idx + 1):
            for sub_y in range(0, len(self.match_layers)):
                sub_match = self.match_layers[sub_y][x + sub_idx]
                if not sub_match.is_finished:
                    continue

                if not sub_match.check_stability([
                    match.energy_layer_name,
                ]):
                    breakpoint()
                    pass

        new_concept = self.concepts[x + idx]
        new_size = 1
        sub_match = None

        for match_layer in reversed(self.match_layers):
            if match_layer[x + idx].is_finished:
                new_concept = match_layer[x + idx].pattern_name
                new_size = match_layer[x + idx].size
                sub_match = match_layer[x + idx]
                break
        
        match.add_concept(new_concept, sub_match, layers)
        match.size += new_size

        print(x, y, new_concept, match.size, match.is_finished, match.is_failed)
        breakpoint()

        if match.is_finished:
            self.process(x, y + 1, 0, call_stack)
        elif match.is_failed:
            size = match.size - new_size
            match.reset()
            if not call_stack:
                call_stack.append((x, y, 0))
                self.process(x + size, 0, 0, call_stack)
            else:
                x, y, idx = call_stack.pop()
                self.process(x, y, idx, call_stack)
        else:
            self.process(x, y, idx + new_size, call_stack)

    def match(self):
        y = 0
        x = 0
        self.process(x, y)
        return
        while True:
            if y == 0:
                for word in self.concepts:
                    self.match_layers[y][x].add_cocnept(word)
                    if self.match_layers[y][x].is_finished():
                        y += 1
                        break
                    breakpoint()
                    pass
            else:
                pass
            breakpoint()
            pass


mt = MatchTree(sentence, aeg)
mt.match()
