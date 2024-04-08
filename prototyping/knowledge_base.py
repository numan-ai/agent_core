import enum
import functools
import json
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, List

from shpat.hierarchy import HierarchyProvider
from neomodel import db, config


# config.DATABASE_URL = "bolt://neo4j:test@localhost:7687"
config.DATABASE_URL = "bolt://neo4j:4t3e2s1t@95.179.224.85:7687"


class Cardinality(enum.Enum):
    ONE = enum.auto()
    LIST = enum.auto()
    DICT = enum.auto()


NO_DEFAULT = object()


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
            id=raw_node.id,
            label=list(raw_node.labels)[0],
            data=node_data,
            metadata=metadata,
        )


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


# counter = Counter()
def patch_cypher(query, *args, **kwargs):
    original_query = query
    # saved_query = re.sub(r'\d+', '*', query)
    # saved_query = re.sub(r'[:]\w+', '*', saved_query)
    # print(query)
    # counter[saved_query] += 1
    return original(original_query, *args, **kwargs)
original = db.cypher_query
db.cypher_query = patch_cypher


class KnowledgeBase:
    @functools.cache
    def find_associations(self, center: int, bidirectional=True) -> list[KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a)-[r:associated*]-{'' if bidirectional else '>'}(b)
                WHERE id(a) = {center}
                RETURN b""")

        return [
            KBNode.create(row[0])
            for row in results
        ]

    @functools.cache
    def find_direct_associations(self, center: int, bidirectional=True) -> list[KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a)-[r:associated]-{'' if bidirectional else '>'}(b)
                    WHERE id(a) = {center}
                    RETURN b""")

        return [
            KBNode.create(row[0])
            for row in results
        ]

    @functools.cache
    def find_word(self, word: str, return_none: bool = True) -> Optional[KBNode]:
        field = {"value": word}

        field = dict_to_fields(field)

        results, columns = db.cypher_query(
            f"""MATCH (a:Word{field}) RETURN a""")

        if len(results) == 0:
            if return_none:
                return None
            else:
                raise KeyError(f"Word {word} not found")

        return KBNode.create(results[0][0])

    @staticmethod
    def build_hierarchy():
        results, columns = db.cypher_query(
            """MATCH (a:Concept) -[r:parent*]-> (b:Concept) RETURN a, b""")

        parents = defaultdict(list)
        children = defaultdict(list)
        for child, parent in results:
            parents[child['name']].append(parent['name'])
            children[parent['name']].append(child['name'])

        return parents, children

    @staticmethod
    def build_direct_hierarchy():
        results, columns = db.cypher_query(
            """MATCH (a:Concept) -[r:parent]-> (b:Concept) RETURN a, b""")

        parents = defaultdict(list)
        children = defaultdict(list)
        for child, parent in results:
            parents[child['name']].append(parent['name'])
            children[parent['name']].append(child['name'])

        return parents, children

    @functools.cache
    def find_concept(self, concept_uuid: str, return_none: bool = False) -> KBNode:
        field = {"name": concept_uuid}

        field = dict_to_fields(field)

        results, columns = db.cypher_query(
            f"""MATCH (a:Concept{field}) RETURN a""")

        if len(results) == 0:
            if return_none:
                return
            raise KeyError(f"Concept '{concept_uuid}' is not found")
        if len(results) > 1:
            raise ValueError(f"Multiple concepts '{concept_uuid}' found")

        return KBNode.create(results[0][0])

    @functools.lru_cache
    def find_children(self, concept_id: int) -> list[KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a:Concept)-[:parent*]->(b:Concept) 
                WHERE id(b)={int(concept_id)}
                RETURN a""")

        return [KBNode.create(x[0]) for x in results]

    @functools.lru_cache
    def find_direct_children(self, concept_id: int) -> list[KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a:Concept)-[:parent]->(b:Concept) 
                    WHERE id(b)={int(concept_id)}
                    RETURN a""")

        return [KBNode.create(x[0]) for x in results]

    @functools.lru_cache
    def find_parents(self, concept_id: int) -> list[KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a:Concept)-[:parent*]->(b:Concept) 
                    WHERE id(a)={int(concept_id)}
                    RETURN b""")

        return [KBNode.create(x[0]) for x in results]

    @functools.lru_cache
    def find_direct_parents(self, concept_id: int) -> list[KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a:Concept)-[:parent]->(b:Concept) 
                        WHERE id(a)={int(concept_id)}
                        RETURN b""")

        return [KBNode.create(x[0]) for x in results]

    @functools.cache
    def find_node(self, node_id: int) -> KBNode:
        results, columns = db.cypher_query(
            f"""MATCH (a) WHERE id(a)={int(node_id)} RETURN a""")

        return KBNode.create(results[0][0])

    @functools.cache
    def in_(self, node_id: int, edge_name: str) -> list[KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a)-[r:{edge_name}]->(b) WHERE id(b)={int(node_id)} RETURN a""")

        return [KBNode.create(row[0]) for row in results]
    
    @functools.cache
    def out(self, node_id: int, edge_name: str) -> list[KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a)-[r:{edge_name}]->(b) WHERE id(a)={int(node_id)} RETURN b""")

        return [KBNode.create(row[0]) for row in results]

    @functools.cache
    def out_dict(self, node_id: int, edge_name: str) -> dict[str, KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a)-[r:{edge_name}]->(b) WHERE id(a)={int(node_id)} RETURN r, b""")

        return {edge['name']: KBNode.create(node) for edge, node in results}

    @functools.cache
    def out_dict_pair(self, node_id: int, edge_name: str) -> dict[str, KBNode]:
        results, columns = db.cypher_query(
            f"""MATCH (a)-[r:{edge_name}]->(b) WHERE id(a)={int(node_id)} RETURN r, b""")

        return {edge['name']: (edge, KBNode.create(node)) for edge, node in results}

    # def delete_node(self, node_id):
    #     print('Delete node', node_id)
    #     db.cypher_query(
    #         f"MATCH (n) WHERE id(n)={int(node_id)} DETACH DELETE n")
    #
    # def copy_edge(self, node_id, start, end):
    #     print('Copy edge', int(node_id), int(start), int(end))
    #     edge = self.find_edge_by_id(node_id)
    #     return self.create_edge(edge.type, start, end, dict(edge))
    #
    # def copy_node(self, node_id):
    #     print('Copy node', int(node_id))
    #     node = self._find_node_by_id(node_id)
    #     return self.create_node(list(node.labels)[0], dict(node))
    #
    # @functools.lru_cache
    # def _find_node_by_id(self, node_id):
    #     if node_id is None:
    #         raise ValueError(f'Node id can\'t be None')
    #     results, columns = db.cypher_query(
    #         f"MATCH (n) WHERE id(n)={int(node_id)} RETURN *")
    #     try:
    #         return results[0][0]
    #     except IndexError:
    #         raise ValueError(f"Node is not found: {node_id}")
    #
    # def find_node_by_id(self, node_id):
    #     node = self._find_node_by_id(node_id)
    #     return Entity(
    #         self.ctx,
    #         list(node.labels)[0],
    #         dict(node),
    #         kb_node_id=node.id
    #     )
    #
    # def node_id_search(self, label, fields):
    #     fields = dict_to_fields(fields)
    #     results, columns = db.cypher_query(
    #         f"MATCH (n:{label} {fields}) RETURN *")
    #     return [x[0].id for x in results]
    #
    # def find_edge_by_id(self, edge_id):
    #     print('Find edge', edge_id)
    #     results, columns = db.cypher_query(
    #         f"MATCH (a)-[r]->(b) WHERE id(r)={int(edge_id)} RETURN r")
    #     return results[0][0]
    #
    
    def get_outcomes(self, node_id):
        results, columns = db.cypher_query(
            f"""MATCH (a:Concept)-[:outcome]->(b:Outcome)-[:act]->(c:Concept) WHERE id(c)={int(node_id)} RETURN a, b""")

        results = [
            (KBNode.create(row[0]), KBNode.create(row[1]))
            for row in results
        ]

        return results
    
    def create_node(self, name, fields, x=None, y=None):
        print(f'---Creating node: {name} {fields}')

        if '_meta' not in fields:
            meta = {
                'x': x or random.randint(0, 10000),
                'y': y or random.randint(0, 10000)
            }
            fields['_meta'] = json.dumps(meta)

        fields = dict_to_fields(fields)
        results, columns = db.cypher_query(
            f"CREATE (n:{name} {fields}) RETURN *")

        self.find_node.cache_clear()
        self.find_word.cache_clear()

        return KBNode.create(results[0][0])

    def create_edge(self, name, start_id: int, end_id: int, fields):
        """ Does not create duplicates """
        print(f'---Creating edge {name}: {int(start_id)}->{int(end_id)}')
        fields = dict_to_fields(fields)
        results, columns = db.cypher_query(
            f"""MATCH (a), (b)
                WHERE id(a) = {int(start_id)} AND id(b) = {int(end_id)}
                MERGE (a)-[r:{name} {fields}]->(b)
                RETURN r""")

        return results[0][0]
    #
    # def does_edge_exist(self, start: int, name: str, end: int):
    #     results, columns = db.cypher_query(
    #         f"""MATCH (a)-[r:{name}]-(b)
    #             WHERE id(a) = {start} AND id(b) = {end}
    #             RETURN r""")
    #     return len(results) > 0
    #
    # @functools.lru_cache
    # def find_concept_id(self, name: str):
    #     concept = Concept.nodes.get_or_none(name=name)
    #     if concept is None:
    #         raise ValueError(f"Concept not found: name={name}")
    #     return concept.id
    #
    # @functools.lru_cache
    # def find_concept_name(self, concept_id: int):
    #     results, columns = db.cypher_query(
    #         f"MATCH (a:Concept) WHERE id(a) = {concept_id} RETURN a")
    #
    #     try:
    #         return results[0][0]['name']
    #     except IndexError:
    #         raise ValueError(f"Concept not found: id={concept_id}")
    #
    #     raise ValueError(f"Field is not found: {concept}->{name}")
    #
    # def search(self, concept: str, fields):
    #     # print('Search', concept, fields)
    #     fields_str = ' AND '.join([
    #         f'a.{key}="{value}"'
    #         for key, value in fields.items()
    #     ])
    #     results, columns = db.cypher_query(
    #         f"MATCH (a:{concept}) WHERE {fields_str} RETURN a")
    #
    #     node = results[0][0]
    #
    #     yield Entity(self.ctx, concept, dict(node), kb_node_id=node.id)
    #
    # def set_node_field(self, node_id, field, value):
    #     db.cypher_query(f"MATCH (n) WHERE id(n) = {int(node_id)} SET n.{field} = '{value}' RETURN n")
    #
    # def edge_out(self, edge_id: str):
    #     # print('Edge out', edge_id)
    #     results, columns = db.cypher_query(
    #         f"MATCH (a)-[r]->(b) WHERE id(r)={int(edge_id)} RETURN b")
    #
    #     try:
    #         return results[0][0]
    #     except IndexError:
    #         breakpoint()
    #         pass
    #
    # def node_out(self, node_id: str, edge_name=None) -> list[int]:
    #     return [
    #         x.id for x in self._node_out(node_id, edge_name)
    #     ]
    #
    # @functools.lru_cache
    # def _node_out(self,
    #               node_id: str,
    #               edge_name=None,
    #               edge_filters: Optional[tuple[tuple[str, any]]] = None):
    #     if edge_filters is None:
    #         filters = ""
    #     else:
    #         filters = dict_to_fields(dict(edge_filters))
    #
    #     if edge_name:
    #         results, columns = db.cypher_query(
    #             f"MATCH (a)-[r:{edge_name} {filters}]->(b) WHERE id(a)={int(node_id)} RETURN b")
    #     else:
    #         results, columns = db.cypher_query(
    #             f"MATCH (a)-[r {filters}]->(b) WHERE id(a)={int(node_id)} RETURN b")
    #
    #     return [
    #         x[0] for x in results
    #     ]
    #
    # @functools.lru_cache
    # def node_out_dict(self, node_id: str, edge_name=None):
    #     if edge_name:
    #         results, columns = db.cypher_query(
    #             f"MATCH (a)-[r:{edge_name}]->(b) WHERE id(a)={int(node_id)} RETURN b, r")
    #     else:
    #         results, columns = db.cypher_query(
    #             f"MATCH (a)-[r]->(b) WHERE id(a)={int(node_id)} RETURN b, r")
    #
    #     ids = {
    #         x[1].get('name', ''): x[0].id for x in results
    #     }
    #     return ids
    #
    # def node_out_edges(self, node_id: str, edge_name=None):
    #     # print('Node out', node_id, edge_name)
    #     if edge_name:
    #         results, columns = db.cypher_query(
    #             f"MATCH (a)-[r:{edge_name}]->(b) WHERE id(a)={int(node_id)} RETURN r")
    #     else:
    #         results, columns = db.cypher_query(
    #             f"MATCH (a)-[r]->(b) WHERE id(a)={int(node_id)} RETURN r")
    #
    #     return [
    #         x[0].id for x in results
    #     ]
    #
    # @functools.lru_cache
    # def _out(self, node_id, edge):
    #     results, columns = db.cypher_query(
    #         f"MATCH (a)-[r:{edge}]->(b) WHERE id(a)={int(node_id)} RETURN r, b")
    #     return results
    #
    # def out_old(self, node_id: str, edge: str, cardinality: Cardinality = Cardinality.ONE):
    #     # print('Out', node_id, edge, cardinality)
    #     results = self._out(node_id, edge)
    #
    #     if cardinality is Cardinality.ONE:
    #         if len(results) != 1:
    #             breakpoint()
    #         rel, end = results[0]
    #         return Entity(self.ctx, list(end.labels)[0], dict(end), kb_node_id=end.id)
    #
    #     if cardinality is Cardinality.LIST:
    #         result = []
    #         for rel, end in results:
    #             result.append(Entity(
    #                 self.ctx,
    #                 list(end.labels)[0],
    #                 dict(end),
    #                 kb_node_id=end.id
    #             ))
    #
    #         return Entity(self.ctx, 'List', {
    #             "value": result
    #         })
    #
    #     if cardinality is Cardinality.DICT:
    #         result = {}
    #         for rel, end in results:
    #             key = rel.get('name', '')
    #             if key in result:
    #                 raise ValueError(f"Duplicated edge `{edge}[{key}]` in node {int(node_id)}")
    #             result[key] = (Entity(
    #                 self.ctx,
    #                 list(end.labels)[0],
    #                 dict(end),
    #                 kb_node_id=end.id
    #             ))
    #
    #         return Entity(self.ctx, 'Dict', {
    #             "value": result
    #         })
    #
    #     raise NotImplementedError()


# TODO: don't use instances, replace with classmethods or functions
kb = KnowledgeBase()


class KBHierarchy(HierarchyProvider):
    @functools.lru_cache
    def get_parents(self, concept: str) -> List[str]:
        try:
            node = kb.find_concept(concept)
        except KeyError:
            return []
        return [x.data['name'] for x in kb.find_parents(node.id)]

    @functools.lru_cache
    def get_children(self, concept: str) -> List[str]:
        try:
            node = kb.find_concept(concept)
        except KeyError:
            return []
        return [x.data['name'] for x in kb.find_children(node.id)]
