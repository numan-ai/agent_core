import abc
from dataclasses import dataclass
import uuid


FIELD_VALUE_EMPTY = object()


class WorldModelNode(abc.ABC):
    def __init__(self, *, instance_id=None):
        self.id = instance_id or str(uuid.uuid4())
        
    @abc.abstractmethod
    def copy(self):
        pass


@dataclass
class WorldModelEdge:
    start: str
    end: str
    name: str


@dataclass
class InstanceReference:
    instance_id: str
    
    
@dataclass
class InstanceFieldReference:
    instance_id: str
    field_name: str


class InstanceField(WorldModelNode):
    def __init__(self, name, world_model) -> None:
        super().__init__()
        self.name = name
        self.world_model = world_model
        self._value = FIELD_VALUE_EMPTY
        
    @property
    def value(self):
        if self._value is FIELD_VALUE_EMPTY:
            return self.world_model.out_one(self.id, "__value__")
        return self._value
    
    @value.setter
    def value(self, value):
        assert not isinstance(value, WorldModelNode)
        self._value = value
        
    def copy(self):
        field = InstanceField(self.name, self.world_model)
        field.id = self.id
        field.value = self._value
        return field
        
    def __repr__(self) -> str:
        if self._value is FIELD_VALUE_EMPTY:
            return f"<Field {self.name}>"
        return f"<Field {self.name}=[{self._value}]>"