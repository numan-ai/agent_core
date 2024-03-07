from typing import Optional
from src.base_module import AgentModule


import os
import abc
import enum
import functools

from dataclasses import dataclass, field

from neomodel import db, config
from dotenv import load_dotenv

from .concept import Concept


load_dotenv()

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]

config.DATABASE_URL = f"bolt://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"


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
    # Field -> Task
    FEX_OUT = "fex_out"
    # Field -> Concept
    FIELD_CONCEPT = "concept"
    # Field -> Task
    FIELD_GETTER = "getter"
    # Field -> Field
    FIELD_REVERSE = "reverse"
    REACTION = "reaction"
    
    
class KBNodeType(enum.Enum):
    CONCEPT = "Concept"
    FIELD = "Field"
    
    
class KBEdgeDirection(enum.Enum):
    OUT = enum.auto()
    IN = enum.auto()
    ANY = enum.auto()


@dataclass
class KBNode:
    id: int
    label: str
    data: dict
    metadata: dict = field(repr=False, default_factory=dict)
    
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
    id: int
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
    def find_concept(self, cid: str, should_raise: bool = True) -> KBNode:
        concept_name = Concept.get_name(cid)
        nodes = self.find_nodes(KBNodeType.CONCEPT, (
            ("name", concept_name),
        ))
        
        # len(nodes) > 1 is critical, so raise
        if len(nodes) > 1:
            raise KBIntegrityError(f"Multiple concepts with name '{concept_name}' found")
        
        if not nodes:
            if should_raise:
                raise KBNotFoundError(f"Concept '{concept_name}' not found")
            return None
        
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
    def out_dict2(self, node_id: int, edge_type: KBEdgeType, 
                  edge_filters: tuple, key: str, direction: KBEdgeDirection, 
                  direct=True) -> dict[str, KBNode]:
        pass
    
    @abc.abstractmethod
    def find_nodes(self, node_type: KBNodeType, filters: tuple) -> list[KBNode]:
        pass

    @abc.abstractmethod
    def get_node(self, node_id: int) -> KBNode:
        pass
    
    @abc.abstractmethod
    def new_node(self, label: str, data: dict) -> KBNode:
        pass
    
    @abc.abstractmethod
    def new_edge(self, label: str, start_node_id: int, end_node_id: int, data: dict) -> KBEdge:
        pass
    
    @abc.abstractmethod
    def get_field(self, concept_id: str, field_name: str) -> Optional[KBNode]:
        pass


def dict_to_fields(dct: dict):
    result = ""
    
    for i, (key, value) in enumerate(dct.items()):
        if i != 0:
            result += ', '
        if isinstance(value, str):
            result += f'{key}: \'{value}\''
        else:
            result += f'{key}: {value}'
    return f"{{{result}}}"


class KnowledgeBase(BaseKnowledgeBase, AgentModule):
    @functools.cache
    def out(self, node_id: int, edge_type: KBEdgeType, 
            edge_filters: tuple = None, direction: KBEdgeDirection = KBEdgeDirection.OUT, 
            direct=True) -> list[KBNode]:
        left_arr = "-" if direction == KBEdgeDirection.OUT else "<-"
        right_arr = "->" if direction == KBEdgeDirection.OUT else "-"
        
        edge_filters = dict_to_fields(dict(edge_filters)) if edge_filters else ""
        
        results, columns = db.cypher_query(
            f"""MATCH (a){left_arr}[r:{edge_type.value}{edge_filters}]{right_arr}(b) WHERE id(a)={int(node_id)} RETURN b""")

        return [KBNode.create(row[0]) for row in results]
    
    @functools.cache
    def out_dict(self, node_id: int, edge_type: KBEdgeType, 
                 edge_filters: tuple = None, key: str = 'name', direction: KBEdgeDirection = KBEdgeDirection.OUT, 
                 direct=True) -> dict[str, KBNode]:
        """ Takes names from the edges """
        left_arr = "-" if direction == KBEdgeDirection.OUT else "<-"
        right_arr = "->" if direction == KBEdgeDirection.OUT else "-"
        
        results, columns = db.cypher_query(
            f"""MATCH (a){left_arr}[r:{edge_type.value}]{right_arr}(b) WHERE id(a)={int(node_id)} RETURN r, b""")

        return {edge['name']: KBNode.create(node) for edge, node in results}
    
    @functools.cache
    def out_dict2(self, node_id: int, edge_type: KBEdgeType, 
                 edge_filters: tuple = None, key: str = 'name', direction: KBEdgeDirection = KBEdgeDirection.OUT, 
                 direct=True) -> dict[str, KBNode]:
        """ Takes names from the nodes """
        left_arr = "-" if direction == KBEdgeDirection.OUT else "<-"
        right_arr = "->" if direction == KBEdgeDirection.OUT else "-"
        
        results, columns = db.cypher_query(
            f"""MATCH (a){left_arr}[r:{edge_type.value}]{right_arr}(b) WHERE id(a)={int(node_id)} RETURN b""")

        nodes = [KBNode.create(result[0]) for result in results]
        return {node.data['name']: node for node in nodes}
    
    @functools.cache
    def find_nodes(self, node_type: KBNodeType, filters: tuple) -> list[KBNode]:
        filters = dict_to_fields(dict(filters))
        
        node_label = node_type.value
        
        results, columns = db.cypher_query(
            f"""MATCH (a:{node_label}{filters}) RETURN a""")

        return [
            KBNode.create(row[0]) for row in results
        ]

    def get_node(self, node_id: int) -> KBNode:
        results, columns = db.cypher_query(
            f"""MATCH (a) WHERE id(a)={int(node_id)} RETURN a""")

        return KBNode.create(results[0][0])
    
    @functools.cache
    def get_outcomes(self, node_id):
        results, columns = db.cypher_query(
            f"""MATCH (a:Concept)-[:outcome]->(b:Outcome)-[:act]->(c:Concept) WHERE id(c)={int(node_id)} RETURN a, b""")

        results = [
            (KBNode.create(row[0]), KBNode.create(row[1]))
            for row in results
        ]

        return results
    
    @functools.cache
    def get_word(self, word: str):
        results, columns = db.cypher_query(
            f"""MATCH (a:Word {{name: '{word}'}}) RETURN a""")

        return KBNode.create(results[0][0])
    
    def new_node(self, label: str, data: dict) -> KBNode:
        data = dict_to_fields(data)
        
        results, columns = db.cypher_query(
            f"""CREATE (a:{label} {data}) RETURN a""")

        return KBNode.create(results[0][0])

    def new_edge(self, label: str, start_node_id: int, end_node_id: int, data: dict) -> KBEdge:
        data = dict_to_fields(data)
        
        results, columns = db.cypher_query(
            f"""MATCH (a), (b) WHERE id(a)={int(start_node_id)} AND id(b)={int(end_node_id)} CREATE (a)-[r:{label} {data}]->(b) RETURN r""")

        return KBEdge(
            id=results[0][0].element_id,
            label=label,
            start_id=start_node_id,
            end_id=end_node_id,
            data=data,
        )
        
    def upsert_edge(self, edge_label: str, start_node_id: int, end_node_id: int, data: dict) -> KBEdge:
        data = dict_to_fields(data)
        
        results, columns = db.cypher_query(
            f"""MATCH (a), (b) WHERE id(a)={int(start_node_id)} AND id(b)={int(end_node_id)} MERGE (a)-[r:{edge_label} {data}]->(b) RETURN r""")

        return KBEdge(
            id=results[0][0].element_id,
            label=edge_label,
            start_id=start_node_id,
            end_id=end_node_id,
            data=data,
        )
        
    def update_node_data(self, node_id: int, data: dict):
        data = dict_to_fields(data)
        
        results, columns = db.cypher_query(
            f"""MATCH (a) WHERE id(a)={int(node_id)} SET a += {data} RETURN a""")

        return KBNode.create(results[0][0])
    
    def get_field(self, concept_id: str, field_name: str) -> Optional[KBNode]:
        raise NotImplementedError()