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
