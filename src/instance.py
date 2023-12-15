import uuid

from dataclasses import dataclass, field

from src.concept import Concept


@dataclass
class Instance:
    concept_name: str
    fields: dict[str, any] = field(default_factory=dict)
    uiid: str = field(repr=False, init=False, default=None)
    
    def __post_init__(self):
        # set Unique Instance ID
        instance_id = uuid.uuid4().hex
        self.uiid = f"{self.concept_name}__{instance_id}"
        
    def get_concept(self) -> Concept:
        return Concept(self.concept_name, {
            field_name: field_value.get_concept()
            for field_name, field_value in self.fields.items()  
            if isinstance(field_value, Instance)
        })
        
    @classmethod
    def from_dict(cls, concept_name: str, data: dict):
        concept_name = Concept.get_name(concept_name)
        fields = {}
        for field_name, field_value in data.items():
            if field_name.startswith('__'):
                continue
            if isinstance(field_value, dict):
                fields[field_name] = Instance.from_dict(field_value['name'], field_value['data'])
            elif isinstance(field_value, list):
                fields[field_name] = [
                    Instance.from_dict(item['name'], item['data']) 
                    if isinstance(item, dict) 
                    else item
                    for item in field_value
                ]
            else:
                fields[field_name] = field_value
                
        return cls(concept_name, fields)
    
    def pprint(self, level=0):
        # recursively print the instance
        """
        Example:
        >>> instance.pprint()
        ActOnEntity {
            act=PrintAct {},
            entity=BinaryMathExpression {
                left=Number {
                    value=1
                },
                right=Number {
                    value=2
                },
                operator=AddOperator {},
            },
        }
        """
        indent = '    ' * level
        print(f'{indent}{self.concept_name} {{')
        for field_name, field_value in self.fields.items():
            if isinstance(field_value, Instance):
                field_value.pprint(level + 1)
            elif isinstance(field_value, list):
                print(f'{indent}    {field_name}=[{", ".join([str(item) for item in field_value])}]')
            else:
                print(f'{indent}    {field_name}={field_value}')
                
        print(f'{indent}}}')
        
        
