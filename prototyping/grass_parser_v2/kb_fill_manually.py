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

""".strip()

cache_file_path = './prototyping/grass_parser_v2/word_concept_cache.json'


def tokenize(sentence):
    tokens = []
    token_positions = []
    token = []
    token_type = None
    
    for idx, char in enumerate(sentence):
        if char == ' ':
            new_token_type = 'space'
            create_token = False
        elif char.isalnum():
            new_token_type = 'alphanumeric'
            create_token = new_token_type != token_type
        else:
            new_token_type = 'special'
            create_token = True
            
        if new_token_type == 'space':
            # ignore spaces
            new_token_type = None
                
        if create_token:
            if token:
                tokens.append("".join(token))
                token_positions.append(idx - len(token))
            token = []
            
        token.append(char)
        
        token_type = new_token_type
        
    if token:
        tokens.append("".join(token))
        token_positions.append(idx - len(token) + 1)
        
    return tokens, token_positions


def load_known_tokens():
    with open(cache_file_path, 'r') as f:
        known_tokens = json.load(f)
        
    new = {
        "sentences": [],
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


def ask_token_concept_llm():
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of fast language models",
            }
        ],
        model="llama3-8b-8192",
    )

    print(chat_completion.choices[0].message.content)


def ask_token_concept(sentence, token, token_pos, defaults):
    token_size = len(token)
    print(sentence[:token_pos], end='')
    # red color
    print("\x1b[31m" + token + "\x1b[0m", end='')
    print(sentence[token_pos + token_size:]) 
    print(' ' * token_pos + '^')
    
    if len(defaults) == 1:
        value = input(f"Enter concept [{defaults[0]}]: ")
    elif defaults:
        value = input(f"Enter concept {defaults}: ")
    else:
        value = input("Enter concept: ")
    
    if len(defaults) == 1 and not value:
        return defaults[0]
    
    assert value, "Concept cannot be empty"
    
    return value


def fix_mistake(known_tokens):
    token = input("Enter token: ")
    concept = input("Enter concept: ")
    known_tokens[token] = concept
    save_known_tokens(known_tokens)


def main():
    sentences = """
        The cat sleeps on the warm windowsill.
        Did you hear that loud noise last night?
        She quickly ran to the store before it closed.
        Tomorrow, we are going to the zoo.
        He often forgets his keys.
        Can you help me with this puzzle?
        The sun rises early in the summer.
        They were laughing at the funny movie.
        I have never seen such a beautiful painting.
        Birds fly south during the winter.
    """
    
    ctx = load_known_tokens()
    ctx_tok = ctx['tokens']
    ctx_sent = ctx['sentences']
    
    start = False
    
    for sentence in sentences.split("\n"):
        sentence = sentence.strip().lower()
        tokens, token_positions = tokenize(sentence)
        
        for token_idx, token in enumerate(tokens):
            if token in ctx_tok and not start:
                continue
            start = True
            
            concept = ask_token_concept(
                sentence, tokens[token_idx],
                token_positions[token_idx],
                defaults=list(ctx_tok.get(token, {}).keys())
            )
            
            if concept == '-':
                continue
            
            if concept == '!':
                fix_mistake(ctx)
                continue
            
            if sentence not in ctx_sent:
                ctx_sent.append(sentence)
                
            sentence_idx = ctx_sent.index(sentence)
            
            ctx_tok[token][concept] = (sentence_idx, token_idx)
            save_known_tokens(ctx)


if __name__ == "__main__":
    main()
