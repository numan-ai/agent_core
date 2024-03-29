import re
import ast

from src.world_model.instance import Instance


BIN_OP_MAP = {
    ast.Add: 'AST_OpPlus',
}

CAMEL_TO_SNAKE = re.compile(r'(?<!^)(?=[A-Z])')


def _camel_to_snake(name: str):
    return CAMEL_TO_SNAKE.sub('_', name).lower()

class Converter:
    def _convert(self, ast_node):
        method_name = f"_convert_{_camel_to_snake(type(ast_node).__name__)}"
        
        if hasattr(self, method_name):
            instance_tree = getattr(self, method_name)(ast_node)
            return instance_tree
        elif ast_node is None:
            return self._convert_none()
        else:
            print(f" - Implementation needed for: {method_name}")
            print(f"AST name: {ast_node}")
            pass

    def _convert_name(self, ast_node: ast.Name):
        return Instance("String", {"value":ast_node.id})
        #return ast_node.id
    def _convert_str(self, ast_node: str):
        return Instance("String", {"value":ast_node})
    
    def _convert_attribute(self, ast_node: ast.Attribute):
        value = ast_node.value
        instance = Instance("AST_Attribute", {"value":self._convert(value), "attr":ast_node.attr})
        return instance

    def _convert_bin_op(self, ast_node: ast.BinOp):
        op = BIN_OP_MAP[type(ast_node.op)]
        instance = Instance("AST_BinOp", {"left": self._convert(ast_node.left),
                                      "op": Instance(op),
                                      "right": self._convert(ast_node.right)})
        return instance
    
    def _convert_constant(self, ast_node: ast.Constant):
        return Instance("Number", {"value": ast_node.value})
        #return ast_node.value

    def _convert_assign(self, ast_node: ast.Assign):
        #print(ast_node.targets[0].id, "=", ast_node.value.value.id)

        print("Here's an assign:",ast_node)
        
        #self.instance_tree.append(instance)

        value = self._convert(ast_node.value)
        for target in ast_node.targets:
            instance = Instance("AST_Assign", {"target":self._convert(target), "value":value})
            #if isinstance(target, ast.Tuple):
            #    for elt in target.elts:
            #        node_target = self._convert(elt)
            #        self.edges.append(Edge(node.id, node_target.id, 'targets'))

        ###node_value = self._convert(ast_node.value)

        #self._last_nodes = [node, ]
    
        return instance
    

    def convert(self, func_def: ast.FunctionDef) -> Instance:
        instance = Instance("AST_FunctionDef", {"name" : self._convert(func_def.name), 
                                            "arguments" : None,
                                            "body" : []})
        
        ###
        #instance.fields["body"] = self._convert(func_def.body[0])
        #return instance
        ###

        for ast_node in func_def.body:
            #last_nodes = self._last_nodes.copy()
            instance.fields["body"].append(self._convert(ast_node))

            #for last_node in last_nodes:
            #    self.edges.append(Edge(last_node.id, node.id, str(uuid4()), 'next'))

        return instance

def convert(ast_graph: ast.FunctionDef):
    cnv = Converter()
    return cnv.convert(ast_graph)



code = """
def f():
    a = test.arg1
    b = a + 1
    test.arg2 = b
"""

ast_graph = ast.parse(code)
print("\n",ast.dump(ast_graph, indent=4),"\n")

funcs = []
for ast_func in ast_graph.body:
    converted = convert(ast_func)
    funcs.append(converted)

    print(converted)
