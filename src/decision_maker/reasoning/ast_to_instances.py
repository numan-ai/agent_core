import re
import ast

from src.world_model.instance import Instance


BIN_OP_MAP = {
    ast.Add: 'AST_OpPlus',
    ast.Sub: 'AST_OpMinus',
    ast.Div: 'AST_OpDividedBy',
    ast.Mult: 'AST_OpMultipliedBy',
    ast.Pow: 'AST_OpToThePowerOf'
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
            instances = getattr(self, method_name)(ast_node)
            return instances
        elif ast_node is None:
            return self._convert_none()
        else:
            print(f" - Implementation needed for: {method_name}")
            print(f"AST name: {ast_node}")
            raise NotImplementedError()

    def _convert_arg(self, ast_arg: ast.arg):
        return Instance("AST_Argument", {"value":ast_arg.arg})

    def _convert_arguments(self, ast_arguments: ast.arguments): # This only converts args. Not posonlyargs, kwonlyargs, kw_defaults or defaults
        return self._convert(ast_arguments.args)

    def _convert_lambda(self, ast_lambda: ast.Lambda):
        instance = Instance("AST_Lambda", {"args":self._convert(ast_lambda.args),
                                           "body":self._convert(ast_lambda.body)})
        return instance

    def _convert_return(self, ast_return: ast.Return):
        return Instance("AST_Return", {"value":self._convert(ast_return.value)})

    def _convert_call(self, ast_call: ast.Call):
        instance = Instance("AST_Call", {"func":self._convert(ast_call.func),
                                         "args":self._convert(ast_call.args),
                                        "keywords":self._convert(ast_call.keywords)})
        return instance

    def _convert_expr(self, ast_expr: ast.expr):
        return self._convert(ast_expr.value)

    def _convert_list(self, ast_list: ast.List):
        if type(ast_list) == ast.List:
            ast_list = ast_list.elts
        return [self._convert(ast_node) for ast_node in ast_list]
    
    def _convert_tuple(self, ast_tuple: ast.Tuple):
        return tuple(self._convert(ast_node) for ast_node in ast_tuple.elts)

    def _convert_name(self, ast_node: ast.Name):
        return Instance("AST_Variable", {"value":ast_node.id})

    def _convert_str(self, ast_node: str):
        return Instance("String", {"value":ast_node})
    
    def _convert_attribute(self, ast_node: ast.Attribute):
        instance = Instance("AST_Attribute", {"value":self._convert(ast_node.value),
                                              "attr":self._convert(ast_node.attr)})
        return instance

    def _convert_bin_op(self, ast_node: ast.BinOp):
        op = BIN_OP_MAP[type(ast_node.op)]
        instance = Instance("AST_BinOp", {"left": self._convert(ast_node.left),
                                      "op": Instance(op),
                                      "right": self._convert(ast_node.right)})
        return instance
    
    def _convert_constant(self, ast_node: ast.Constant):
        if type(ast_node.value) == str:
            return Instance("String", {"value": ast_node.value})
        else:
            return Instance("Number", {"value": ast_node.value})

    def _convert_assign(self, ast_node: ast.Assign):
        if type((target:=ast_node.targets)[0]) != ast.Name:
            raise NotImplementedError("Can't assign to multiple variables yet")
        instance = Instance("AST_Assign", {"target":self._convert(target),
                                           "value":self._convert(ast_node.value)})

        return instance
    

    def _convert_function_def(self, func_def: ast.FunctionDef) -> Instance:
        instance = Instance("AST_FunctionDef", {"name" : self._convert(func_def.name), 
                                            "arguments" : self._convert(func_def.args),
                                            "body" : self._convert(func_def.body)})
        return instance

    def convert(self, ast_graph):
        return self._convert(ast_graph)

def convert(ast_graph: ast.FunctionDef):
    return Converter().convert(ast_graph)


if __name__ == "__main__":
    code = """
a.b
    """

    ast_graph = ast.parse(code)
    print(f"\n\n    INPUT AST\n\n{ast.dump(ast_graph, indent=4)}\n")

    print(f"\n    OUTPUT NESTED INSTANCES\n")
    print(convert(ast_graph.body))
