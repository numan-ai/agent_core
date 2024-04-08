import re
import ast

from src.world_model.instance import Instance
from src.action_manager.module import string_to_instance as String


BIN_OP_MAP = {
    ast.Add: 'AST_OpAdd',
    ast.Sub: 'AST_OpSub',
    ast.Div: 'AST_OpDiv',
    ast.Mult: 'AST_OpMult',
    ast.Pow: 'AST_OpPow',
    ast.Mod: 'AST_OpMod',
}

CMP_OP_MAP = {
    ast.Eq: 'AST_OpEq',
    ast.NotEq: 'AST_OpNotEq',
    ast.Lt: 'AST_OpLt',
    ast.LtE: 'AST_OpLtE',
    ast.Gt: 'AST_OpGt',
    ast.GtE: 'AST_OpGtE',
}

BOOL_OP_MAP = {
    ast.And: 'AST_OpAnd',
    ast.Or: 'AST_OpOr',
    ast.Not: 'AST_OpNot',
}

CAMEL_TO_SNAKE = re.compile(r'(?<!^)(?=[A-Z])')


def _camel_to_snake(name: str):
    return CAMEL_TO_SNAKE.sub('_', name).lower()


class IASTConverter:
    def _convert(self, ast_node):
        """ Recursively converts ast nodes to world model instances.
        Takes any given node like ast.Attribute and it searches in its methods
        if it has something for it, like in this case, it would be _convert_attribute

        If we have the method, we call it and return it, if not, we tell the user that it's missing
        """
        node_type_name = type(ast_node).__name__
        method_name = f"_convert_{_camel_to_snake(node_type_name)}"

        if hasattr(self, method_name):
            instances = getattr(self, method_name)(ast_node)
            return instances
        else:
            raise NotImplementedError(f"Implementation needed for: {method_name}")

    def _convert_bool_op(self, ast_bool_op: ast.BoolOp):
        return Instance("AST_BoolOp", {
            "op": Instance(BOOL_OP_MAP[type(ast_bool_op.op)]),
            "values": [
                self._convert(value) for value in ast_bool_op.values
            ]
        })

    def _convert_arg(self, ast_arg: ast.arg):
        return Instance("AST_Argument", {"value": ast_arg.arg})
    
    def _convert_keyword(self, ast_keyword: ast.keyword):
        return Instance("AST_Keyword", {
            "arg": String(ast_keyword.arg),
            "value": self._convert(ast_keyword.value)
        })

    def _convert_arguments(self, ast_arguments: ast.arguments):
        """ Converts args.
        Does not convert posonlyargs, kwonlyargs, kw_defaults or defaults
        """
        return [
            self._convert(arg) for arg in ast_arguments.args
        ]

    def _convert_return(self, ast_return: ast.Return):
        return Instance("AST_Return", {
            "value": self._convert(ast_return.value)
        })

    def _convert_call(self, ast_call: ast.Call):
        instance = Instance("AST_Call", {
            "func": self._convert(ast_call.func),
            "args": [
                self._convert(arg) for arg in ast_call.args
            ],
            "keywords": [
                self._convert(keyword) for keyword in ast_call.keywords
            ]
        })
        return instance

    def _convert_expr(self, ast_expr: ast.expr):
        return self._convert(ast_expr.value)

    def _convert_list(self, ast_list: ast.List):
        if isinstance(ast_list, ast.List):
            ast_list = ast_list.elts
        return Instance("AST_List", {
            "value": [
                self._convert(ast_node) for ast_node in ast_list
            ]
        })

    def _convert_tuple(self, ast_tuple: ast.Tuple):
        return Instance("AST_Tuple", {
            "value": [
                self._convert(ast_node) for ast_node in ast_tuple.elts
            ]
        })

    def _convert_name(self, ast_node: ast.Name):
        return Instance("AST_Variable", {
            "value": ast_node.id
        })

    def _convert_str(self, ast_node: str):
        return Instance("String", {
            "value": ast_node
        })

    def _convert_attribute(self, ast_node: ast.Attribute):
        instance = Instance("AST_Attribute", {
            "value": self._convert(ast_node.value),
            "attr": self._convert(ast_node.attr)
        })
        return instance

    def _convert_bin_op(self, ast_node: ast.BinOp):
        op = BIN_OP_MAP[type(ast_node.op)]
        instance = Instance("AST_BinOp", {
            "left": self._convert(ast_node.left),
            "op": Instance(op),
            "right": self._convert(ast_node.right)
        })
        return instance

    def _convert_constant(self, ast_node: ast.Constant):
        if isinstance(ast_node.value, str):
            return Instance("String", {"value": ast_node.value})
        elif isinstance(ast_node.value, int):
            return Instance("Number", {"value": ast_node.value})
        else:
            raise NotImplementedError(f"Can't convert constant of type {type(ast_node.value)}")

    def _convert_assign(self, ast_node: ast.Assign):
        if len(ast_node.targets) > 1:
            raise NotImplementedError("Can't assign to multiple variables")
        
        return Instance("AST_Assign", {
            "target": self._convert(ast_node.targets[0]),
            "value": self._convert(ast_node.value)
        })
        
    def _convert_aug_assign(self, ast_node: ast.AugAssign):
        return Instance("AST_AugAssign", {
            "target": self._convert(ast_node.target),
            "value": self._convert(ast_node.value),
            "op": Instance(BIN_OP_MAP[type(ast_node.op)])
        })
    
    def _convert_compare(self, ast_node: ast.Compare):
        if len(ast_node.comparators) > 1:
            raise NotImplementedError("Can't compare multiple values")
        if len(ast_node.ops) > 2:
            raise NotImplementedError("Can't compare more than two values")
        
        return Instance("AST_Compare", {
            "left": self._convert(ast_node.left),
            "op": Instance(CMP_OP_MAP[type(ast_node.ops[0])]),
            "right": self._convert(ast_node.comparators[0]),
        })

    def _convert_if(self, ast_node: ast.If):
        return Instance("AST_If", {
            "test": self._convert(ast_node.test),
            "body": [
                self._convert(node) for node in ast_node.body
            ],
            "orelse": [
                self._convert(node) for node in ast_node.orelse
            ]
        })
        
    def _convert_for(self, ast_node: ast.For):
        return Instance("AST_For", {
            "target": self._convert(ast_node.target),
            "iter": self._convert(ast_node.iter),
            "body": [
                self._convert(node) for node in ast_node.body
            ]
        })
        
    def _convert_while(self, ast_node: ast.While):
        return Instance("AST_While", {
            "test": self._convert(ast_node.test),
            "body": [
                self._convert(node) for node in ast_node.body
            ]
        })

    def _convert_function_def(self, func_def: ast.FunctionDef) -> Instance:
        instance = Instance("AST_FunctionDef", {
            "name": self._convert(func_def.name),
            "arguments": self._convert(func_def.args),
            "body": [
                self._convert(node) for node in func_def.body                                             
            ]
        })
        return instance

    def convert(self, ast_func_def: ast.FunctionDef):
        if not isinstance(ast_func_def, ast.FunctionDef):
            raise ValueError(f"Expected ast.FunctionDef, got {type(ast_func_def)}")
        
        return self._convert(ast_func_def)


def iast_convert(ast_graph: ast.FunctionDef):
    return IASTConverter().convert(ast_graph)
