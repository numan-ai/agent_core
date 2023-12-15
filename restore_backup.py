import json

from src.knowledge_base import db, dict_to_fields


def main(path: object) -> object:
    with open(path) as f:
        data = json.load(f)
        
    node_id_map = {}

    for node in data['nodes']:
        print('node', node['elementId'])
        old_node_id = int(node['elementId'])
        label = node['label']
        properties = node['properties']
        result = db.cypher_query(f"""CREATE (a:{label} {dict_to_fields(properties)}) RETURN a""")
        new_node_id = result[0][0][0].element_id
        node_id_map[old_node_id] = new_node_id
        
    for edge in data['edges']:
        print('edge', edge['elementId'])
        label = edge['type']
        properties = edge['properties']
        start_node_id = int(edge['startNodeElementId'])
        end_node_id = int(edge['endNodeElementId'])
        start_node_id = node_id_map[start_node_id]
        end_node_id = node_id_map[end_node_id]
        db.cypher_query(f"""MATCH (a), (b) WHERE id(a)={start_node_id} AND id(b)={end_node_id} CREATE (a)-[r:{label} {dict_to_fields(properties)}]->(b) RETURN r""")
    


if __name__ == '__main__':
    main("../agent_v6.0/backups/28Nov2023.json")
