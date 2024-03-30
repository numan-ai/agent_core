import ast

from src.decision_maker.reasoning.ast_to_instances import convert
from src.world_model.instance import Instance
from src.action_manager.module import string_to_instance as String
from src.action_manager.module import number_to_instance as Number

#@pytest.fixture(scope="session")
#def ugi():
#    "if you need you can put things inside here that reloads and it's given as a parameter per each test"


def test_functions():#ugi):
    code = """
def f():
    a = test.arg1
    b = a + 1
    test.arg2 = b
"""
    expected_instance = [
        Instance('AST_FunctionDef', {
            'name': String('f'),
            'arguments': [],
            'body': [
                Instance('AST_Assign', {
                    'target': [String('a')],
                    'value': Instance('AST_Attribute', {
                        'value': String('test'),
                        'attr': String('arg1'),
                    }),
                }),
                Instance('AST_Assign', {
                    'target': [String('b')],
                    'value': Instance('AST_BinOp', {
                        'left': String('a'),
                        'op': Instance('AST_OpPlus'),
                        'right': Number(1),
                    }),
                }),
                Instance('AST_Assign', {
                    'target': [
                        Instance('AST_Attribute', {
                            'value': String('test'),
                            'attr': String('arg2'),
                        })
                    ],
                    'value': String('b'),
                })
            ],
        })
    ]
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body) == expected_instance


def test_lists():
    code = """
def f():
    a = test.arg1

def g():
    b = [3 + 1]
"""
    expected_instance = [
        Instance('AST_FunctionDef', {
            'name': String('f'),
            'arguments': [],
            'body': [
                Instance('AST_Assign', {
                    'target': [String('a')],
                    'value': Instance('AST_Attribute', {
                        'value': String('test'),
                        'attr': String('arg1'),
                    }),
                })
            ],
        }),
        Instance('AST_FunctionDef', {
            'name': String('g'),
            'arguments': [],
            'body': [
                Instance('AST_Assign', {
                    'target': [String('b')],
                    'value': [
                        Instance('AST_BinOp', {
                            'left': Number(3),
                            'op': Instance('AST_OpPlus'),
                            'right': Number(1),
                        })
                    ],
                })
            ],
        })
    ]
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body) == expected_instance


def test_tuples():
    code = """
b = (3 + 1,)
"""
    expected_instance = [
        Instance('AST_Assign', {
            'target': [String('b')],
            'value': (
                Instance('AST_BinOp', {
                    'left': Number(3),
                    'op': Instance('AST_OpPlus'),
                    'right': Number(1),
                }),
            ),
        })
    ]
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body) == expected_instance


def test_concatenation():
    code = """
'A' + 'B'
"""
    expected_instance = [
        Instance('AST_BinOp', {
            'left': Number('A'),
            'op': Instance('AST_OpPlus'),
            'right': Number('B'),
        })
    ]
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body) == expected_instance


def test_time_for_math():
    code = """
x = 3
y = x**5*2/1+5-1
"""
    expected_instance = [
        Instance('AST_Assign', {
            'target': [String('x')],
            'value': Number(3),
        }),
        Instance('AST_Assign', {
            'target': [String('y')],
            'value': Instance('AST_BinOp', {
                'left': Instance('AST_BinOp', {
                    'left': Instance('AST_BinOp', {
                        'left': Instance('AST_BinOp', {
                            'left': Instance('AST_BinOp', {
                                'left': String('x'),
                                'op': Instance('AST_OpToThePowerOf'),
                                'right': Number(5),
                            }),
                            'op': Instance('AST_OpMultipliedBy'),
                            'right': Number(2),
                        }),
                        'op': Instance('AST_OpDividedBy'),
                        'right': Number(1),
                    }),
                    'op': Instance('AST_OpPlus'),
                    'right': Number(5),
                }),
                'op': Instance('AST_OpMinus'),
                'right': Number(1),
            }),
        }),
    ]
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body) == expected_instance


def test_func_nesting():
    code = "f(3 + f(3 + f(3 + f(3 + 5))))"
    expected_instance = [
        Instance('AST_Call', {
            'func': String('f'),
            'args': [
                Instance('AST_BinOp', {
                    'left': Number(3),
                    'op': Instance('AST_OpPlus'),
                    'right': Instance('AST_Call', {
                        'func': String('f'),
                        'args': [
                            Instance('AST_BinOp', {
                                'left': Number(3),
                                'op': Instance('AST_OpPlus'),
                                'right': Instance('AST_Call', {
                                    'func': String('f'),
                                    'args': [
                                        Instance('AST_BinOp', {
                                            'left': Number(3),
                                            'op': Instance('AST_OpPlus'),
                                            'right': Instance('AST_Call', {
                                                'func': String('f'),
                                                'args': [
                                                    Instance('AST_BinOp', {
                                                        'left': Number(3),
                                                        'op': Instance('AST_OpPlus'),
                                                        'right': Number(5),
                                                    })
                                                ],
                                                'keywords': [],
                                            }),
                                        })
                                    ],
                                    'keywords': [],
                                }),
                            })
                        ],
                        'keywords': [],
                    }),
                })
            ],
            'keywords': [],
        }),
    ]
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body) == expected_instance

def test_returning():
    code = """
def f(x):
    return x+2
"""
    expected_instance = [
        Instance('AST_FunctionDef', {
            'name': String('f'),
            'arguments': [
                Instance('AST_argument', {
                    'value': 'x',
                })
            ],
            'body': [
                Instance('AST_Return', {
                    'value': Instance('AST_BinOp', {
                        'left': String('x'),
                        'op': Instance('AST_OpPlus'),
                        'right': Number(2),
                    }),
                })
            ],
        })
    ]
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body) == expected_instance

def test_lambda_functions():
    code = """
p = lambda p1, p2, r: p1 + r * (p2 - p1)
"""
    expected_instance = [
        Instance('AST_Assign', {
            'target': [String('p')],
            'value': Instance('AST_Lambda', {
                'args': [
                    Instance('AST_argument', {
                        'value': 'p1',
                    }),
                    Instance('AST_argument', {
                        'value': 'p2',
                    }),
                    Instance('AST_argument', {
                        'value': 'r',
                    })
                ],
                'body': Instance('AST_BinOp', {
                    'left': String('p1'),
                    'op': Instance('AST_OpPlus'),
                    'right': Instance('AST_BinOp', {
                        'left': String('r'),
                        'op': Instance('AST_OpMultipliedBy'),
                        'right': Instance('AST_BinOp', {
                            'left': String('p2'),
                            'op': Instance('AST_OpMinus'),
                            'right': String('p1'),
                        }),
                    }),
                }),
            }),
        }),
    ]
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body) == expected_instance