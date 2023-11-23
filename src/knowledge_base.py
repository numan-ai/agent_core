import functools
import os

from src.interfaces import BaseKnowledgeBase
from src import KBEdgeType, KBNodeType, KBEdgeDirection, KBNode

from neomodel import db, config
from dotenv import load_dotenv


load_dotenv()

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]

config.DATABASE_URL = f"bolt://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"


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


class KnowledgeBase(BaseKnowledgeBase):
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
        left_arr = "-" if direction == KBEdgeDirection.OUT else "<-"
        right_arr = "->" if direction == KBEdgeDirection.OUT else "-"
        
        results, columns = db.cypher_query(
            f"""MATCH (a){left_arr}[r:{edge_type.value}]{right_arr}(b) WHERE id(a)={int(node_id)} RETURN r, b""")

        return {edge['name']: KBNode.create(node) for edge, node in results}
    
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
