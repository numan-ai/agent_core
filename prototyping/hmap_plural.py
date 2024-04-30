"""
we [run]
he [run]s

one [cat]
two [cat]s

1. words can be identified partially (rolling SWI with LPB)
2. SWI - sequential word identification? (directed weigthed hyper graph)
3. LPB - local pyramid building? (try to fully understand available sequence before proceeding further)
4. expanding options (look for a new option only when exhausted all the previous options)
5. one option at a time?? (somehow we don't have many options when trying to understand a sentence,
                           because usually we take the context into account)
6. general discussion context influence options (we don't want to rank them though)
7. preceeding/surrounding words context influence options (we don't want ot rank them though)

how can context influence without ranking all the options? energy based context I think is the solution.
how can we identify words sequencially?
directed weighted hyper graph needs to be combined with an energy graph.


energy is for concepts. if a concept is very active, then it word's hyper edge will have priority.
is it going to be rail-switch like? we decide which path to go on every "hyper edge split"?
no, the path can change completely during the traversal. this is only achievable only with 
energy-based approach for letters and word hyper-edges.

hyper-edge matches need to account the ontology.
energy-based system can handle this.
we add energy up through the ontology, activating all the hyper edges of the parents.
one option is to add energy based on a match, revoking it if the match is revoked.

since the location of letters plays a role on the word activation we need
to somehow account for the location of the letters in the word hyper-edges activation.
"""

from typing import Hashable
from grass import AssociativeEnergyGraph


class AssociativeEnergyHyperGraph(AssociativeEnergyGraph):
    def __init__(self, edges: list[tuple[Hashable, Hashable, float]], 
                 hyper_edges: list[tuple[Hashable, tuple[Hashable]]],
                 bidirectional: bool):
        super().__init__(edges=edges, bidirectional=bidirectional)
        self.hyper_edges = hyper_edges

eag = AssociativeEnergyHyperGraph(edges=[
    # ("Word_he")
], hyper_edges=[
    ("Word_he", ("Letter_H", "Letter_E")),
    ("Word_is", ("Letter_I", "Letter_S")),
    ("Word_hello", ("Letter_H", "Letter_E", "Letter_L", "Letter_L", "Letter_O")),
], bidirectional=False)

breakpoint()
pass
