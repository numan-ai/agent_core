import json
from shpat.hierarchy import StaticKBHierarchy
from shpat.knowledge_base import KnowledgeBase
from shpat.presets.commands_v6 import PATTERNS
from shpat.presets.syntactic_extractor_v6 import SyntacticExtractor
from src.state_manager import StageManager

kb = KnowledgeBase()
hierarchy = StaticKBHierarchy(kb)
hierarchy.prefetch()
sm = StageManager(kb, hierarchy)


def parse(text, debug=False):
    text = f' {text} '
    extractor = SyntacticExtractor(PATTERNS, hierarchy=hierarchy, stage_manager=sm)
    extractor.process(text)

    if debug:
        extractor.print_matches()
            
    extractor.matches[1].sort(key=lambda x: (x.size, len(json.dumps(x.structure))))

    for match in extractor.matches[1][::-1]:
        if match.concept not in {'AlphaNumeric'}:
            break
    else:
        raise ValueError("No match found")
    structure = match.structure

    print(f'parsed "{text}" as \n\t', match)

    if match.size != (len(text) - 2):
        raise ValueError("Didn't parse the whole sentence")

    return {
        "name": match.concept,
        "data": structure
    }


def main():
    structure = parse(" create file named main.py ")

    breakpoint()
    pass


if __name__ == '__main__':
    main()
