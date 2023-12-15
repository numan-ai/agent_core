import json
import random
from shpat import Extractor, Match, Pattern, PatternNode
from shpat.hierarchy import DictHierarchyProvider

from src.world_model.world_model import WorldModel


PATTERNS = [
    Pattern("Digit", [
        PatternNode("Character", ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']),
    ]),
    Pattern("Number", nodes=[
        PatternNode("Digit", many=True),
    ], pre=[
        PatternNode("Character", " "),
    ], post=[
        PatternNode("Character", " "),
    ]),
    Pattern("Letter", [
        PatternNode("Character", ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                                  'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                                  'u', 'v', 'w', 'x', 'y', 'z']),
    ]),
    Pattern("Word", nodes=[
        PatternNode("Letter", many=True),
    ], pre=[
        PatternNode("Character", " "),
    ], post=[
        PatternNode("Character", " "),
    ]),
    Pattern("Verb", [
        PatternNode("Word", ["run", "walk", "sleep"]),
    ]),
    Pattern("Adjective", [
        PatternNode("Word", ["red", "blue", "green"]),
    ]),
    Pattern("Adverb", [
        PatternNode("Word", ["quickly", "slowly", "quietly"]),
    ]),
    Pattern("Noun", [
        PatternNode("Word", ["file", "folder", "directory"]),
    ]),
    Pattern("DefiniteArticle", [
        PatternNode("Word", ["the"]),
    ]),
    Pattern("IndefiniteArticle", [
        PatternNode("Word", ["a", "an"]),
    ]),
    Pattern("NounPhrase", [
        PatternNode("Article"),
        PatternNode("Character", " "),
        PatternNode("Noun", id='noun'),
    ]),
]

HIERARCHY = DictHierarchyProvider(children={
    "Article": ["DefiniteArticle", "IndefiniteArticle"],
})


from src.instance import Instance


def main():
    wm = WorldModel()
    wm.expect_event(
        "TestEvent",
        timeout=5,
    )
    
    Instance("Person__Hannah", {
        "owns": [
            Instance("Apple", {})
        ]
    })
    
    Instance("Statement", {
        "subject": Instance("DirectEntityReferenceByName", {
            "name": "Hannah",
            "concept": "Person",
        }),
        "act": Instance("HasAct"),
        "direct_object": Instance("IndefiniteEntityReference", {
            "concept": Instance("Concept", {
                "value": "AppleClass",
            })
        }),
    })
    
    Instance("Statement", {
        "subject": Instance("DirectEntityReferenceByName", {
            "name": "Hannah",
            "concept": "Person",
        }),
        "act": Instance("GiveAct"),
        "direct_object": Instance("IndefiniteEntityReference", {
            "concept": Instance("Concept", {
                "value": "AppleClass",
            })
        }),
        "indirect_object": Instance("DirectEntityReferenceByName", {
            "name": "Mike",
            "concept": "Person",
        }),
    })
    
    breakpoint()
    pass
    exit()
    
    
    extractor = Extractor(PATTERNS, HIERARCHY)
    extractor.process(" a file ")
    extractor.print_matches()
    
    extractor.matches[1].sort(key=lambda x: (x.size, len(json.dumps(x.structure))))
    match = extractor.matches[1][-1]
    
    instance = Instance.from_dict(
        concept_name=match.concept,
        data=match.structure,
    )
    
    breakpoint()
    pass
    
    
if __name__ == '__main__':
    main()