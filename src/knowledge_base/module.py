import os
import abc
import enum
import functools
from typing import Optional
from dataclasses import dataclass, field

from neomodel import db, config
from dotenv import load_dotenv

from .concept import Concept
from src.base_module import AgentModule


load_dotenv()

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]

config.DATABASE_URL = f"bolt://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"


class KBEdgeType(enum.Enum):
    """
    When a class inherits from Enum it becomes a datatype of paired data.
    
    No need to instantiate it, you can use it directly
    KBEdgeType.FIELD (With the name you want)

    To access the value add .value to the end like so:
    KBEdgeType.TASK.value
    """
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
    """
    enum.auto() guarantees that each value will be unique
    """
    OUT = enum.auto()
    IN = enum.auto()
    ANY = enum.auto()


@dataclass
class KBNode:
    """
    @dataclass decorator saves you boilerplate code, lines belows are
    equivalent to doing all the __init__ and self.var = var, etc.

    This KBNode class is what the KB will use to manage knowledge


    field is being used in here to assign a default value of an empty dict,
    it's being used because otherwise every instance of KBNode would share
    the same default dictionary
    """
    id: int
    label: str
    data: dict
    metadata: dict = field(repr=False, default_factory=dict)
    
    @classmethod
    def create(cls, raw_node):
        """
        raw_node is a Neo4j Node in Cypher_Query syntax

        I think guidelines indicate that it should be named
        from_raw_node, but create might be more appropiate and intuitive
        """
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
    """
    When a class inherits from Exception it turns into a custom Exception
    class
    """
    pass    

    
class KBIntegrityError(Exception):
    pass


class KBNotFoundError(Exception):
    pass


class BaseKnowledgeBase(abc.ABC):
    """
    Inheritance from ABC is just so we can use @abstractmethod
    """
    def find_concept(self, cid: str, should_raise: bool = True) -> KBNode:
        """
        Finds and returns a KBNode, I ignore what cid should be
        """
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
    
    """
    All these @abstractmethod mean that the child has to define those
    methods itself, otherwise it will raise a TypeError
    I think we can ignore them since child will overwrite them
    """
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
    """
    Turns given dict into a string written like a dict,
    only change is that it gets rid of keys's quotation marks
    """
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
    """
    Classes separated by commas indicates a multiple inheritance

    What @cache does is remembering the result of a previous computation.
    f(n) is stored so when called again there's no need to run the function
    """
    @functools.cache
    def out(self, node_id: int, edge_type: KBEdgeType, 
            edge_filters: tuple = None, direction: KBEdgeDirection = KBEdgeDirection.OUT, 
            direct=True) -> list[KBNode]:
        """
        You specify a node (a) by its id, this method is going to return
        all nodes (b) that are connected to (a) meeting the other 3
        arguments of edge type, edge filter and direction
        """

        # if direction == KBEdgeDirection.OUT points edge from a to b
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
        """
        Almost the same as above, difference being:
         + returns it in a dict format where
           + key is the name of the edge
           + value is (b)
         - No Edge filter
        """
        left_arr = "-" if direction == KBEdgeDirection.OUT else "<-"
        right_arr = "->" if direction == KBEdgeDirection.OUT else "-"
        
        results, columns = db.cypher_query(
            f"""MATCH (a){left_arr}[r:{edge_type.value}]{right_arr}(b) WHERE id(a)={int(node_id)} RETURN r, b""")

        return {edge['name']: KBNode.create(node) for edge, node in results}
    
    @functools.cache
    def out_dict2(self, node_id: int, edge_type: KBEdgeType, 
                 edge_filters: tuple = None, key: str = 'name', direction: KBEdgeDirection = KBEdgeDirection.OUT, 
                 direct=True) -> dict[str, KBNode]:
        """
        Searches like above but just returns (b)

        nodes is a list of KBNodes based on (b)'s
        returned dict is {KBNode.name:KBNode}
        """
        left_arr = "-" if direction == KBEdgeDirection.OUT else "<-"
        right_arr = "->" if direction == KBEdgeDirection.OUT else "-"
        
        results, columns = db.cypher_query(
            f"""MATCH (a){left_arr}[r:{edge_type.value}]{right_arr}(b) WHERE id(a)={int(node_id)} RETURN b""")

        nodes = [KBNode.create(result[0]) for result in results]
        return {node.data['name']: node for node in nodes}
    
    @functools.cache
    def find_nodes(self, node_type: KBNodeType, filters: tuple) -> list[KBNode]:
        """Find all nodes that match the label and filters"""
        filters = dict_to_fields(dict(filters))
        
        node_label = node_type.value
        
        results, columns = db.cypher_query(
            f"""MATCH (a:{node_label}{filters}) RETURN a""")

        return [
            KBNode.create(row[0]) for row in results
        ]

    def get_node(self, node_id: int) -> KBNode:
        """Search node by id"""
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
        """
        I think this creates edges but only if they don't exist in that
        specific configuration
        """
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
        """Changes the properties of a node"""
        results, columns = db.cypher_query(
            f"""MATCH (a) WHERE id(a)={int(node_id)} SET a += {data} RETURN a""")

        return KBNode.create(results[0][0])
    
    def get_field(self, concept_id: str, field_name: str) -> Optional[KBNode]:
        raise NotImplementedError()