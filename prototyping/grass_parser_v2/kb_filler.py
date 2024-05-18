import json
import openai
from src.knowledge_base import KnowledgeBase


cache_path = "./prototyping/grass_parser_v2/kb_filler_cache.json"
with open(cache_path, "r") as f:
    cache = json.load(f)

prompt = """create a csv of single word {}.
return {} words. don't output any other text. don't return duplicates.
output singular form if it exists.
"""

themes = [
    ("possessive pronouns", "Possessor", 7),
    # ("fruits", "Fruit", 10),
    # ("vegetables", "Vegetable", 10),
    # ("animals", "Animal", 10),
    # ("birds", "Bird", 5),
    # ("fishes", "Fish", 5),
    # ("insects", "Insect", 5),
    # ("flowers", "Flower", 10),
    # ("transports", "Transport", 5),
    # ("colors", "Color", 10),
    # ("shapes", "Shape", 5),
    # ("countries", "Country", 20),
    # ("languages", "Language", 20),
    # ("professions", "Profession", 20),
    # ("sports", "Sport", 10),
    # ("musical_instruments", "MusicalInstrument", 10),
    # ("clothes", "Clothing", 10),
]

kb = KnowledgeBase(None)

y = 5000


for theme, parent_name, count in themes:
    print("Processing:", parent_name)
    x = 15000

    concept_names = cache.get(parent_name)

    if concept_names is None:
        response = openai.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt.format(theme, count)},
            ],
            model="gpt-4o",
        )
        csv_data = response.choices[0].message.content

        csv_data = csv_data.strip('`')
        
        concept_names = csv_data.replace(',', '\n').strip().split('\n')
        if concept_names and concept_names[0] == 'csv':
            concept_names = concept_names[1:]

        concept_names = [
            concept_name.capitalize()
            for concept_name in concept_names
            if concept_name.capitalize() != parent_name.capitalize() and 
            concept_name.capitalize() not in {"Plaintext", "Word"} and 
            concept_name.isalpha()
        ]

        print(parent_name, concept_names)

        val = input("y/n: ")

        if val != "y":
            print("skipping")
            continue

        cache[parent_name] = concept_names
        with open(cache_path, "w") as f:
            json.dump(cache, f)

    mean_x = x + 200 * (len(concept_names) - 1) / 2 + 200
    parent = kb.upsert_concept(parent_name, mean_x, y - 400)

    for concept_name in concept_names:
        x += 200
        concept = kb.upsert_concept(f"{concept_name}{parent_name}", x, y)
        kb.upsert_edge("parents", concept.id, parent.id, {})

    y += 1000
