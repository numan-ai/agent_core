import re

from dataclasses import dataclass, field


cid_pattern = re.compile(r'\w+|[!"#$%&\'()*+,\-./:;<=>?@[\]^_`{|}~]')


@dataclass
class Concept:
    name: str
    fields: dict[str, 'Concept'] = field(default_factory=dict)

    def get_cid(self):
        cid = [self.name, ]

        if self.fields:
            cid.append('{')
            for key, value in sorted(self.fields.items(), key=lambda x: x[0]):
                if isinstance(value, list):
                    breakpoint()
                cid.append(f'{key}={value.get_cid()},')
            cid[-1] = cid[-1][:-1]
            cid.append('}')

        return ''.join(cid)

    @classmethod
    def _from_tokens(cls, tokens: list[str]) -> 'Concept':
        name = tokens.pop()

        fields = {}

        if tokens[-1] != '{':
            return Concept(name)

        tokens.pop()  # {
        while tokens:
            field_name = tokens.pop()
            if field_name == '}':
                break
            tokens.pop()  # '='
            field_value = cls._from_tokens(tokens)
            fields[field_name] = field_value
            if tokens and tokens[-1] == ',':
                tokens.pop()

        return Concept(name, fields)

    @classmethod
    def from_cid(cls, cid: str) -> 'Concept':
        if '{' not in cid:
            return Concept(cid)

        tokens = re.findall(cid_pattern, cid.strip())[::-1]
        concept = cls._from_tokens(tokens)
        return concept

    @classmethod
    def pprint(cls, cid: str):
        tokens = re.findall(cid_pattern, cid.strip())
        indent = 0
        tokens_len = len(tokens)
        for idx, token in enumerate(tokens):
            if token == '}':
                print('\n' + (indent - 1) * '    ', end='')
            print(token, end='')

            if token == '{':
                indent += 1
                print('\n' + indent * '    ', end='')
            elif token == '}':
                indent -= 1
                if tokens_len < idx + 1 and tokens[idx + 1] != ',':
                    print('\n' + indent * '    ', end='')
            elif token == ',':
                print('\n' + indent * '    ', end='')
        print('\n')

    @classmethod
    def get_name(cls, cid: str):
        if '{' in cid:
            name = cid[:cid.index('{')]
        else:
            name = cid
        
        return name

    def to_concept_instance(self):
        from src.world_model.instance import Instance
        return Instance("Concept", {
            "name": self.name,
            "fields": {
                field_name: field_value.to_concept_instance()
                for field_name, field_value in self.fields.items()
            }
        })

    def __repr__(self):
        if self.fields:
            return f"Concept(name='{self.name}', fields={self.fields})"
        return f"Concept(name='{self.name}')"
    