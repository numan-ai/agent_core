import ast

from src.decision_maker.reasoning.ast_to_iast import iast_convert
from src.world_model.instance import Instance
from src.action_manager.module import string_to_instance as String
from src.action_manager.module import number_to_instance as Number


def test_iast_converter_assign():
    code = """
def main():
    a = test.arg1
    b = a + 1
    test.arg2 = b
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_Attribute', {
                    'value': Instance("AST_Variable", {"value": "test"}),
                    'attr': String('arg1'),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "b"}),
                'value': Instance('AST_BinOp', {
                    'left': Instance("AST_Variable", {"value": "a"}),
                    'op': Instance('AST_OpAdd'),
                    'right': Number(1),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance('AST_Attribute', {
                    'value': Instance("AST_Variable", {"value": "test"}),
                    'attr': String('arg2'),
                }),
                'value': Instance("AST_Variable", {"value": "b"}),
            })
        ],
    })
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance


def test_iast_converter_list():
    code = """
def main():
    b = [3 + 1]
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "b"}),
                'value': Instance('AST_List', {
                    'value': [
                        Instance('AST_BinOp', {
                            'left': Number(3),
                            'op': Instance('AST_OpAdd'),
                            'right': Number(1),
                        })
                    ]
                }),
            })
        ],
    })
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance


def test_iast_converter_tuple():
    code = """
def main():
    b = (3 + 1,)
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "b"}),
                'value': Instance('AST_Tuple', {
                    'value': [
                        Instance('AST_BinOp', {
                            'left': Number(3),
                            'op': Instance('AST_OpAdd'),
                            'right': Number(1),
                        })
                    ]
                }),
            })
        ],
    })
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance


def test_iast_converter_bin_op():
    code = """
def main():
    a = a + (b / 10)
    a = f(a) - b
    a = a * b.d
    a = a.c.d / b.test()
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_BinOp', {
                    'left': Instance("AST_Variable", {"value": "a"}),
                    'op': Instance('AST_OpAdd'),
                    'right': Instance('AST_BinOp', {
                        'left': Instance("AST_Variable", {"value": "b"}),
                        'op': Instance('AST_OpDiv'),
                        'right': Number(10),
                    }),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_BinOp', {
                    'left': Instance('AST_Call', {
                        'func': Instance("AST_Variable", {"value": "f"}),
                        'args': [Instance("AST_Variable", {"value": "a"})],
                        'keywords': [],
                    }),
                    'op': Instance('AST_OpSub'),
                    'right': Instance("AST_Variable", {"value": "b"}),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_BinOp', {
                    'left': Instance("AST_Variable", {"value": "a"}),
                    'op': Instance('AST_OpMult'),
                    'right': Instance('AST_Attribute', {
                        'value': Instance("AST_Variable", {"value": "b"}),
                        'attr': String('d'),
                    }),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_BinOp', {
                    'left': Instance('AST_Attribute', {
                        'value': Instance("AST_Attribute", {
                            'value': Instance("AST_Variable", {"value": "a"}),
                            'attr': String('c'),
                        }),
                        'attr': String('d'),
                    }),
                    'op': Instance('AST_OpDiv'),
                    'right': Instance('AST_Call', {
                        'func': Instance('AST_Attribute', {
                            'value': Instance("AST_Variable", {"value": "b"}),
                            'attr': String('test'),
                        }),
                        'args': [],
                        'keywords': [],
                    }),
                }),
            }),
        ],
    })
    ast_module = ast.parse(code)
    
    assert iast_convert(ast_module.body[0]) == expected_instance


def test_iast_converter_nested_call():
    code = """
def main():
    f(3 + f(3 + f(3 + 5)))
"""
    expected_instance = Instance("AST_FunctionDef", {
        "name": String("main"),
        "arguments": [],
        "body": [
            Instance("AST_Call", {
                "func": Instance("AST_Variable", {"value": "f"}),
                "args": [
                    Instance("AST_BinOp", {
                        "left": Number(3),
                        "op": Instance("AST_OpAdd"),
                        "right": Instance("AST_Call", {
                            "func": Instance("AST_Variable", {"value": "f"}),
                            "args": [
                                Instance("AST_BinOp", {
                                    "left": Number(3),
                                    "op": Instance("AST_OpAdd"),
                                    "right": Instance("AST_Call", {
                                        "func": Instance("AST_Variable", {"value": "f"}),
                                        "args": [
                                            Instance("AST_BinOp", {
                                                "left": Number(3),
                                                "op": Instance("AST_OpAdd"),
                                                "right": Number(5),
                                            }),
                                        ],
                                        "keywords": [],
                                    }),
                                }),
                            ],
                            "keywords": [],
                        }),
                    }),
                ],
                "keywords": [],
            }),
        ],
    })
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance

def test_iast_converter_return():
    code = """
def main(x):
    return x + 2
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [
            Instance('AST_Argument', {
                'value': 'x',
            }),
        ],
        'body': [
            Instance('AST_Return', {
                'value': Instance('AST_BinOp', {
                    'left': Instance('AST_Variable', {
                        'value': 'x',
                    }),
                    'op': Instance('AST_OpAdd'),
                    'right': Number(2),
                }),
            }),
        ],
    })
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance


def test_iast_converter_bool_op():
    code = """
def main():
    return a and (b or c)
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_Return', {
                'value': Instance('AST_BoolOp', {
                    'op': Instance('AST_OpAnd'),
                    'values': [
                        Instance('AST_Variable', {
                            'value': 'a',
                        }),
                        Instance('AST_BoolOp', {
                            'op': Instance('AST_OpOr'),
                            'values': [
                                Instance('AST_Variable', {
                                    'value': 'b',
                                }),
                                Instance('AST_Variable', {
                                    'value': 'c',
                                }),
                            ],
                        }),
                    ],
                }),
            }),
        ],
    })
    
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance
    
    
def test_iast_converter_compare():
    code = """
def main():
    a = a == b
    a = a != b
    a = a < b
    a = a <= b
    a = a > b
    a = a >= b
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_Compare', {
                    'left': Instance("AST_Variable", {"value": "a"}),
                    'op': Instance('AST_OpEq'),
                    'right': Instance("AST_Variable", {"value": "b"}),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_Compare', {
                    'left': Instance("AST_Variable", {"value": "a"}),
                    'op': Instance('AST_OpNotEq'),
                    'right': Instance("AST_Variable", {"value": "b"}),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_Compare', {
                    'left': Instance("AST_Variable", {"value": "a"}),
                    'op': Instance('AST_OpLt'),
                    'right': Instance("AST_Variable", {"value": "b"}),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_Compare', {
                    'left': Instance("AST_Variable", {"value": "a"}),
                    'op': Instance('AST_OpLtE'),
                    'right': Instance("AST_Variable", {"value": "b"}),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_Compare', {
                    'left': Instance("AST_Variable", {"value": "a"}),
                    'op': Instance('AST_OpGt'),
                    'right': Instance("AST_Variable", {"value": "b"}),
                }),
            }),
            Instance('AST_Assign', {
                'target': Instance("AST_Variable", {"value": "a"}),
                'value': Instance('AST_Compare', {
                    'left': Instance("AST_Variable", {"value": "a"}),
                    'op': Instance('AST_OpGtE'),
                    'right': Instance("AST_Variable", {"value": "b"}),
                }),
            }),
        ],
    })
    
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance
    

def test_iast_converter_if():
    code = """
def main():
    if a == b:
        a += 1
        return a
    else:
        a -= 1
        return b
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_If', {
                'test': Instance('AST_Compare', {
                    'left': Instance('AST_Variable', {
                        'value': 'a',
                    }),
                    'op': Instance('AST_OpEq'),
                    'right': Instance('AST_Variable', {
                        'value': 'b',
                    }),
                }),
                'body': [
                    Instance('AST_AugAssign', {
                        'target': Instance('AST_Variable', {
                            'value': 'a',
                        }),
                        'value': Number(1),
                        'op': Instance('AST_OpAdd'),
                    }),
                    Instance('AST_Return', {
                        'value': Instance('AST_Variable', {
                            'value': 'a',
                        }),
                    }),
                ],
                'orelse': [
                    Instance('AST_AugAssign', {
                        'target': Instance('AST_Variable', {
                            'value': 'a',
                        }),
                        'value': Number(1),
                        'op': Instance('AST_OpSub'),
                    }),
                    Instance('AST_Return', {
                        'value': Instance('AST_Variable', {
                            'value': 'b',
                        }),
                    }),
                ],
            }),
        ],
    })
    
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance


def test_iast_converter_for():
    code = """
def main():
    for i in range(10):
        a = 5
        print(a)
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_For', {
                'target': Instance('AST_Variable', {
                    'value': 'i',
                }),
                'iter': Instance('AST_Call', {
                    'func': Instance('AST_Variable', {
                        'value': 'range',
                    }),
                    'args': [Number(10)],
                    'keywords': [],
                }),
                'body': [
                    Instance('AST_Assign', {
                        'target': Instance('AST_Variable', {
                            'value': 'a',
                        }),
                        'value': Number(5),
                    }),
                    Instance('AST_Call', {
                        'func': Instance('AST_Variable', {
                            'value': 'print',
                        }),
                        'args': [Instance('AST_Variable', {
                            'value': 'a',
                        })],
                        'keywords': [],
                    }),
                ],
            }),
        ],
    })

    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance
    

def test_iast_converter_while():
    code = """
def main():
    while a < b:
        a += 1
        b -= 1
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_While', {
                'test': Instance('AST_Compare', {
                    'left': Instance('AST_Variable', {
                        'value': 'a',
                    }),
                    'op': Instance('AST_OpLt'),
                    'right': Instance('AST_Variable', {
                        'value': 'b',
                    }),
                }),
                'body': [
                    Instance('AST_AugAssign', {
                        'target': Instance('AST_Variable', {
                            'value': 'a',
                        }),
                        'value': Number(1),
                        'op': Instance('AST_OpAdd'),
                    }),
                    Instance('AST_AugAssign', {
                        'target': Instance('AST_Variable', {
                            'value': 'b',
                        }),
                        'value': Number(1),
                        'op': Instance('AST_OpSub'),
                    }),
                ],
            }),
        ],
    })
    
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance


def test_iast_converter_func_call_keyword():
    code = """
def main():
    f(4, a=5, b=6)
"""
    expected_instance = Instance('AST_FunctionDef', {
        'name': String('main'),
        'arguments': [],
        'body': [
            Instance('AST_Call', {
                'func': Instance('AST_Variable', {
                    'value': 'f',
                }),
                'args': [Number(4)],
                'keywords': [
                    Instance('AST_Keyword', {
                        'arg': String('a'),
                        'value': Number(5),
                    }),
                    Instance('AST_Keyword', {
                        'arg': String('b'),
                        'value': Number(6),
                    }),
                ],
            }),
        ],
    })
    
    ast_module = ast.parse(code)
    assert iast_convert(ast_module.body[0]) == expected_instance