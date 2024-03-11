from collections import defaultdict
import uuid
from typing import Optional
from dataclasses import dataclass, field

import agci.sst.entities

from src.knowledge_base.module import (
    KBNode, 
    KBEdgeType,
    KBEdgeDirection,
    BaseKnowledgeBase,
)
from src.world_model.instance import Instance
from src.world_model.module import WorldModel


@dataclass
class UNode:
    id: str
    graph: 'UGraph' = field(repr=False)
    underlying: any
    
    
class UKBNode(UNode):
    underlying: KBNode
    

class UKBConceptNode(UNode):
    underlying: KBNode
    
    def get_field(self, field_name: str) -> Optional['UKBFieldNode']:
        kb_field = self.graph.knowledge_base.get_field(
            self.underlying.id, field_name)
        if kb_field is None:
            return None
        
        return UKBFieldNode(
            id=self.graph.get_ukb_node_id(kb_field),
            graph=self.graph,
            underlying=kb_field,
        )
        
    def get_class(self) -> Optional['UKBConceptNode']:
        result = self.graph.knowledge_base.out(
            self.underlying.id, KBEdgeType.CLASS,
            direction=KBEdgeDirection.OUT)
        
        if len(result) != 1:
            return None
        
        return UKBConceptNode(
            id=self.graph.get_ukb_node_id(result[0]),
            graph=self.graph,
            underlying=result[0],
        )
        
    def get_instance(self) -> Optional['UKBConceptNode']:
        result = self.graph.knowledge_base.out(
            self.underlying.id, KBEdgeType.CLASS,
            direction=KBEdgeDirection.IN)
        
        if len(result) != 1:
            return None
        
        return UKBConceptNode(
            id=self.graph.get_ukb_node_id(result[0]),
            graph=self.graph,
            underlying=result[0],
        )
        
    
class UKBFieldNode(UNode):
    underlying: KBNode
    
    def get_concept(self) -> UKBConceptNode:
        result = self.graph.knowledge_base.out(
            self.underlying.id, KBEdgeType.FIELD_NODE,
            direction=KBEdgeDirection.IN)
        
        if len(result) != 1:
            raise ValueError(
                f"Field {self.underlying.id} has {len(result)} concepts")
        
        return UKBConceptNode(
            id=self.graph.get_ukb_node_id(result[0]),
            graph=self.graph,
            underlying=result[0],
        )
        
    def get_field_concept(self) -> UKBConceptNode:
        result = self.graph.knowledge_base.out(
            self.underlying.id, KBEdgeType.FIELD_CONCEPT,
            direction=KBEdgeDirection.OUT)
        
        if len(result) != 1:
            raise ValueError(
                f"Field {self.underlying.id} has {len(result)} field concepts")
        
        return UKBConceptNode(
            id=self.graph.get_ukb_node_id(result[0]),
            graph=self.graph,
            underlying=result[0],
        )
        
    def get_getters(self, field_concept: str):
        getters = self.graph.ac_getters[field_concept]
        return [
            UACNode(
                id=self.graph.get_ac_node_id(getter),
                graph=self.graph,
                underlying=getter,
            )
            for getter in getters
        ]
        
    def get_setters(self, field_concept: str):
        setters = self.graph.ac_setters[field_concept]
        return [
            UACNode(
                id=self.graph.get_ac_node_id(setter),
                graph=self.graph,
                underlying=setter,
            )
            for setter in setters
        ]
    
    
class UACNode(UNode):
    underlying: agci.sst.entities.Node

    
class UWMNode(UNode):
    underlying: Instance
    
    def get_concept(self) -> Optional[UKBConceptNode]:
        result = self.graph.knowledge_base.find_concept(
            self.underlying.concept_name, should_raise=False)
        
        if result is None:
            return None
        
        return UKBConceptNode(
            id=self.graph.get_ukb_node_id(result),
            graph=self.graph,
            underlying=result,
        )
        
    def _find_reverse_field(self, field_name) -> Optional[str]:
        kb_concept = self.graph.knowledge_base.find_concept(
                self.underlying.concept_name, should_raise=False)
        
        if kb_concept is None:
            return None
            
        kb_field = self.graph.knowledge_base.get_field(
            kb_concept.id, field_name)
        
        if kb_field is None:
            return None

        reverse_fields = self.graph.knowledge_base.out(
            kb_field.id, KBEdgeType.FIELD_REVERSE,
            direction=KBEdgeDirection.ANY)
        
        if len(reverse_fields) < 1:
            return None
        
        return reverse_fields[0].data['name']
        
    def get_field_value(self, field_name) -> Optional['UWMNode']:
        try:
            result = self.underlying.fields[field_name]
        except AttributeError:
            reverse_field_name = self._find_reverse_field(field_name)
            
            reverse_edges = self.graph.world_model.incoming_edges(
                self.underlying.id, '__value__')
            
            for reverse_edge in reverse_edges:
                reverse_field_values = self.graph.world_model.incoming_edges(
                    reverse_edge.start, reverse_field_name)
                
                if len(reverse_field_values) < 1:
                    return None
                
                result = self.graph.world_model.get_instance(
                    reverse_field_values[0].start)
                break
            else:
                return None
                
        return UWMNode(
            id=self.graph.get_uwm_node_id(result),
            graph=self.graph,
            underlying=result,
        )


def _get_ac_getters(ac_graph: agci.sst.entities.Graph):
    getters = defaultdict(list)
    
    for node in ac_graph.get_nodes():
        if isinstance(node, agci.sst.entities.Variable) and node.name == 'get_field':
            func_call = ac_graph.in_(node, 'func')[0]
            func_args = ac_graph.out_edges(func_call, 'args')
            func_kwargs = ac_graph.out_edges(func_call, 'kwargs')
            assert not func_kwargs
            assert len(func_args) == 2
            
            _, field = func_args
            
            if not isinstance(field.end, agci.sst.entities.Constant):
                continue
            
            getter_head_id = ac_graph.node_to_function_head[func_call.node_id]
            getter_head = ac_graph.find_node(getter_head_id)
            
            getters[field.end.value].append(getter_head)
    
    return getters



def _get_ac_setters(ac_graph: agci.sst.entities.Graph):
    setters = defaultdict(list)
    
    for node in ac_graph.get_nodes():
        if isinstance(node, agci.sst.entities.Variable) and node.name == 'set_field':
            func_call = ac_graph.in_(node, 'func')[0]
            func_args = ac_graph.out_edges(func_call, 'args')
            func_kwargs = ac_graph.out_edges(func_call, 'kwargs')
            assert not func_kwargs
            assert len(func_args) == 3
            
            _, field, _ = func_args
            
            if not isinstance(field.end, agci.sst.entities.Constant):
                continue
            
            setter_head_id = ac_graph.node_to_function_head[func_call.node_id]
            setter_head = ac_graph.find_node(setter_head_id)
            
            setters[field.end.value].append(setter_head)
    
    return setters


class UGraph:
    def __init__(
        self,
        knowledge_base: BaseKnowledgeBase,
        world_model: WorldModel,
        ac_graph: agci.sst.entities.Graph,
    ) -> None:
        self.knowledge_base = knowledge_base
        self.world_model = world_model
        self.ac_graph = ac_graph
        
        self.ac_getters = _get_ac_getters(self.ac_graph)
        self.ac_setters = _get_ac_setters(self.ac_graph)
        
        self.__kb_ids_to_ug_ids = {}
        self.__ug_ids_to_kb_ids = {}
        
        self.__wm_ids_to_ug_ids = {}
        self.__ug_ids_to_wm_ids = {}
        
        self.__ac_ids_to_ug_ids = {}
        self.__ug_ids_to_ac_ids = {}
        
    def get_concept(self, concept_name) -> Optional[UKBConceptNode]:
        kb_node: KBNode = self.knowledge_base.find_concept(concept_name, should_raise=False)
        if kb_node is None:
            return None
        
        return UKBConceptNode(
            id=self.get_ukb_node_id(kb_node),
            graph=self,
            underlying=kb_node,
        )
        
    def get_wm_instance(self, instance_id) -> Optional[UWMNode]:
        try:
            instance: Instance = self.world_model.get_instance(instance_id)
        except ValueError:
            return None
        
        return UWMNode(
            id=self.get_uwm_node_id(instance),
            graph=self,
            underlying=instance,
        )
        
    def get_ukb_node_id(self, node: KBNode) -> str:
        try:
            ugi_id = self.__kb_ids_to_ug_ids[node.id]
        except KeyError:
            ugi_id = uuid.uuid4().hex
            self.__kb_ids_to_ug_ids[node.id] = ugi_id
            self.__ug_ids_to_kb_ids[ugi_id] = node.id
        
        return ugi_id
    
    def get_uwm_node_id(self, instance: Instance) -> str:
        try:
            ugi_id = self.__wm_ids_to_ug_ids[instance.id]
        except KeyError:
            ugi_id = uuid.uuid4().hex
            self.__wm_ids_to_ug_ids[instance.id] = ugi_id
            self.__ug_ids_to_wm_ids[ugi_id] = instance.id
        
        return ugi_id
    
    def get_ac_node_id(self, node: agci.sst.entities.Node) -> str:
        try:
            ugi_id = self.__ac_ids_to_ug_ids[node.node_id]
        except KeyError:
            ugi_id = uuid.uuid4().hex
            self.__ac_ids_to_ug_ids[node.node_id] = ugi_id
            self.__ug_ids_to_ac_ids[ugi_id] = node.node_id
        
        return ugi_id
