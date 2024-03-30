import pytest, ast
from ast_to_instances import Converter


def convert(ast_graph: ast.FunctionDef):
    return Converter().convert(ast_graph)


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
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body)


def test_lists():
    code = """
def f():
    a = test.arg1

def g():
    b = [3 + 1]
"""
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body)


def test_tuples():
    code = """
b = (3 + 1,)
"""
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body)


def test_concatenation():
    code = """
'A' + 'B'
"""
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body)


def test_time_for_math():
    code = """
x = 3
y = x**5*2/1+5-1
"""
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body)


def test_func_nesting():
    code = "f(3 + b)"
    for _ in range(2):
        code = code.replace("b", code)
    code.replace("b", "5")

    ast_graph = ast.parse(code)
    assert convert(ast_graph.body)

def test_returning():
    code = """
def f(x):
    return x+2
"""
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body)

def test_lambda_functions():
    code = """
p = lambda p1, p2, r: p1 + r * (p2 - p1)
"""
    ast_graph = ast.parse(code)
    assert convert(ast_graph.body)