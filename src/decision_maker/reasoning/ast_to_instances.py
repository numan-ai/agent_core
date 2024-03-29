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
        '''
        The heart of this converter.
        it takes any given node like ast.Attribute and it searches in its methods
        if it has something for it, like in this case, it would be _convert_attribute

        If we have the method, we call it and return it, if not, we tell the user that it's missing
        '''
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

    def _convert_assign(self, ast_node: ast.Assign):
        value = self._convert(ast_node.value)
        for target in ast_node.targets:
            instance = Instance("AST_Assign", {"target":self._convert(target), "value":value})
            # This might or might not need some other approach because as you can see, it only returns the last of this
    
        return instance
    

    def convert(self, func_def: ast.FunctionDef) -> Instance:
        '''
        This is the main way of using this class. You give it an ast.FunctionDef
        and it will explore all of its nodes, per each node it will retreive its
        value or keep calling functions until it reaches something it can run

        We could say that this is completely automatic, error free and kind of recursive.
        '''
        instance = Instance("AST_FunctionDef", {"name" : self._convert(func_def.name), 
                                            "arguments" : None,
                                            "body" : []})

        for ast_node in func_def.body:
            instance.fields["body"].append(self._convert(ast_node))

        return instance

def convert(ast_graph: ast.FunctionDef):
    cnv = Converter()
    return cnv.convert(ast_graph)


if __name__ == "__main__":
    code = """
def f():
    a = test.arg1
    b = a + 1
    test.arg2 = b
    """

    ast_graph = ast.parse(code)
    print(f"\n\n    INPUT AST\n\n{ast.dump(ast_graph, indent=4)}\n")

    print(f"\n    OUTPUT NESTED INSTANCES\n")
    funcs = []
    for ast_func in ast_graph.body:
        converted = convert(ast_func)
        funcs.append(converted)

        print(converted)
