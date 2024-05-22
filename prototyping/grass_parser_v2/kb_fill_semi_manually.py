import os
import json

from collections import defaultdict

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

prompt = """
You are given a sentence that you need to annotate with concepts.
Examples:
Result:
Sentence: The cat sleeps on the warm windowsill.
the, The_DefiniteDeterminer
cat, Cat_PhysicalEntity
sleeps, Sleep_Verb3rd
on, On_Preposition
warm, Warm_DescriptionTemperature
windowsill, Windowsill_PhysicalEntity

Sentence: Did you hear that loud noise last night?
Result:
did, Did_QuestionVerb
you, You_Pronoun
hear, Hear_Verb
that, That_DemonstrativeDeterminer
loud, Loud_DescriptionVolume
noise, Noise_AbstractConcept
last, Last_DescriptionTime
night, Night_TimeOfDay

Sentence: She quickly ran to the construction site before it closed.
Result:
she, She_SubjectivePronoun
quickly, Quickly_AdverbSpeed
ran, Ran_VerbPast
to, To_Preposition
the, The_DefiniteDeterminer
construction site, ConstructionSite_PhysicalLocation
before, Before_Preposition
it, It_SubjectivePronoun
closed, Closed_VerbPast

Some more examples of concepts:
Year_AbstractConceptTimeUnit, Last_DescriptionOrder, Sunday_DayOfWeek, Now_AbstractConceptTimePoint, Apples_PhysicalEntityPlural

Use descriptions for adjectives and similar modifiers.
Describe verbs with their tense, person, etc.
Describe nouns with their plurality, etc.

Other second parts for concepts:
DefiniteDeterminer, PhysicalEntity, TimeOfDay, DayOfWeek, Verb3rd, Preposition, DescriptionTemperature, QuestionVerb, Pronoun, Verb, DemonstrativeDeterminer, DescriptionVolume, AbstractConcept, DescriptionTime, TimeOfDay, SubjectivePronoun, AdverbSpeed, VerbPast, ObjectivePronoun, Entity, PhysicalLocation
If no second part matches, you can come up with a new one.
For example there are possible variations for description: Description, DescriptionColor, DescriptionSize, etc. You can create new ones.

Only output the Result, nothing else, no comments.

Sentence: {}
Result:
""".strip()

cache_file_path = './prototyping/grass_parser_v2/word_concept_cache2.json'


def load_known_tokens():
    with open(cache_file_path, 'r') as f:
        known_tokens = json.load(f)
        
    new = {
        "sentences": known_tokens['sentences'],
        "tokens": defaultdict(dict),
    }
    
    for k, v in known_tokens['tokens'].items():
        new['tokens'][k] = defaultdict(dict)
        for concept, (sentence, token_idx) in v.items():
            new['tokens'][k][concept] = (sentence, token_idx)
    
    save_known_tokens(new)
    return new


def save_known_tokens(known_tokens):
    with open(cache_file_path, 'w') as f:
        json.dump(known_tokens, f, indent=4)


def ask_token_concept_llm(sentence):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt.format(sentence),
            }
        ],
        model="llama3-70b-8192",
    )

    output = chat_completion.choices[0].message.content
    
    lines = output.strip().split("\n")
    result = [
        line.split(",")
        for line in lines
    ]
    result = [
        (token.strip(), concept.strip())
        for token, concept in result
    ]
    
    return result


def main():
    sentences = [
        # "The cat sleeps on the warm windowsill.", 
        # "Did you hear that loud noise last night?", 
        # "She quickly ran to the store before it closed.", 
        # "Tomorrow, we are going to the zoo.", 
        # "He often forgets his keys.", 
        # "Can you help me with this puzzle?", 
        # "The sun rises early in the summer.", 
        # "They were laughing at the funny movie.", 
        # "I have never seen such a beautiful painting.", 
        # "Birds fly south during the winter.", 
        
        # "The cat jumps over the fence.",
        # "She will read her favorite book tomorrow.",
        # "They had walked to the park every Sunday last year.",
        # "He eats an apple every morning for breakfast.",
        # "We are playing soccer in the yard now.",
        # "The sun sets behind the mountains, painting the sky orange.",
        # "She found an old coin while digging in the garden.",
        # "I have never seen such a beautiful rainbow before.",
        # "Can you help me carry these heavy boxes?",
        # "The baby giggled as the dog licked her tiny feet.",
        
        "The cat sleeps on the soft, blue pillow.",
        "She will visit her grandmother next week.",
        "Can you see the bright stars in the sky tonight?",
        "The boy quickly ran to catch the bus.",
        "They were singing happily in the park yesterday.",
        "A large tree grows near the small, quiet pond.",
        "We enjoy playing soccer on sunny days.",
        "He reads a new book every month.",
        "The flowers bloom beautifully in the spring.",
        "Have you ever traveled to a foreign country?",
    ]
    
    ctx = load_known_tokens()
    ctx_tok = ctx['tokens']
    ctx_sent = ctx['sentences']
    
    for sentence in sentences:
        sentence = sentence.strip().lower()
        
        if sentence not in ctx_sent:
            ctx_sent.append(sentence)
            
        result = ask_token_concept_llm(sentence)

        sentence_idx = ctx_sent.index(sentence)
        
        for token, concept in result:
            ctx_tok[token][concept] = (sentence_idx, -1)
        save_known_tokens(ctx)


if __name__ == "__main__":
    main()
