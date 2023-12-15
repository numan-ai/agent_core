from dataclasses import dataclass, field
from functools import partial
import os
from pprint import pprint

import agci
from src.interfaces.base_knowledge_base import KBEdgeType
import src.shpat_commands
from src.knowledge_base import KnowledgeBase
from src.instance import Instance
from src.reference_manager import ReferenceManager
from src.helpers import find_associated_task


@dataclass
class ActionHistoryNode:
    instance: Instance
    children: list['ActionHistoryNode'] = field(default_factory=list)


class ActionHistory:
    def __init__(self) -> None:
        self.children: list[ActionHistoryNode] = []
        self.activity_stack = []
        
    def push(self, instance: Instance):
        new_node = ActionHistoryNode(instance)
        
        if self.activity_stack:
            active_node = self.activity_stack[-1]
            active_node.children.append(new_node)
        else:
            self.children.append(new_node)
        
        self.activity_stack.append(new_node)
        
    def pop(self):
        self.activity_stack.pop()
