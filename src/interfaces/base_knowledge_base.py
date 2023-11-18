import abc
from dataclasses import dataclass, field
import enum

from src.concept import Concept


class KBEdgeType(enum.Enum):
    # Concept -> Concept
    PARENT = "parent"
    # Concept -> Concept
    CLASS = "class"
    # Concept -> Concept
    FIELD = "field"
    # Concept -> Field
    FIELD_NODE = "fields"
    # Concept -> Task
    TASK = "task"
    
    
class KBNodeType(enum.Enum):
    CONCEPT = "Concept"
    FIELD = "Field"
    
    
class KBEdgeDirection(enum.Enum):
    OUT = enum.auto()
    IN = enum.auto()


@dataclass
class KBNode:
    id: int
    label: str
    data: dict
    metadata: dict = field(repr=False)
    
    @classmethod
    def create(cls, raw_node):
        node_data = dict(raw_node)
        metadata = node_data.pop('_meta')

        return cls(
            id=raw_node.element_id,
            label=list(raw_node.labels)[0],
            data=node_data,
            metadata=metadata,
        )
        

@dataclass
class KBEdge:
    label: str
    start_id: int
    end_id: int
    data: dict
    

class KBBaseError(Exception):
    pass    

    
class KBIntegrityError(Exception):
    pass


class KBNotFoundError(Exception):
    pass



class BaseKnowledgeBase(abc.ABC):
    def find_concept(self, cid: str) -> KBNode:
        concept_name = Concept.get_name(cid)
        nodes = self.find_nodes(KBNodeType.CONCEPT, (
            ("name", concept_name),
        ))
        
        if len(nodes) > 1:
            raise KBIntegrityError(f"Multiple concepts with name '{concept_name}' found")
        
        if not nodes:
            raise KBNotFoundError(f"Concept '{concept_name}' not found")
        
        return nodes[0]
    
    def get_parents(self, cid: str, direct=False) -> list[KBNode]:
        node = self.find_concept(cid)
        return self.out(
            node_id=node.id,
            edge_type=KBEdgeType.PARENT,
            edge_filters=None,
            direct=direct,
            direction=KBEdgeDirection.OUT,
        )
    
    def get_children(self, cid: str, direct=False, field_expansion=False) -> list[KBNode]:
        node = self.find_concept(cid)
        
        edge_filters = (
            ("field_expansion", "1"),
        ) if field_expansion else None
        
        return self.out(
            node_id=node.id,
            edge_type=KBEdgeType.PARENT,
            edge_filters=edge_filters,
            direct=direct,
            direction=KBEdgeDirection.IN,
        )
    
    @abc.abstractmethod
    def out(self, node_id: int, edge_type: KBEdgeType, 
            edge_filters: tuple = None, direction: KBEdgeDirection = KBEdgeDirection.OUT, 
            direct=True) -> list[KBNode]:
        pass
    
    @abc.abstractmethod
    def out_dict(self, node_id: int, edge_type: KBEdgeType, 
                 edge_filters: tuple, key: str, direction: KBEdgeDirection, 
                 direct=True) -> dict[str, KBNode]:
        pass
    
    @abc.abstractmethod
    def find_nodes(self, node_type: KBNodeType, filters: tuple) -> list[KBNode]:
        pass

    @abc.abstractmethod
    def get_node(self, node_id: int) -> KBNode:
        pass