def execute_iast(ctx: Context, node: AST_Variable):
    return node.fields.value

def execute_iast(ctx: Context, node: String):
    return node.fields.value

def execute_iast(ctx: Context, node: Number):
    return node.fields.value

def execute_iast(ctx: Context, node: AST_Attribute):
    exec(f"{execute_iast(node.fields.value)}.{execute_iast(node.fields.attr)}")

def execute_iast(ctx: Context, node: AST_BinOp):
    match node.fields.op.concept_name:
        case "AST_OpPlus":
            result =  node.fields.left + node.fields.right
        case "AST_OpMinus":
            result =  node.fields.left - node.fields.right
        case "AST_OpMultipliedBy":
            result =  node.fields.left * node.fields.right
        case "AST_OpDividedBy":
            result =  node.fields.left / node.fields.right
        case "AST_OpToThePowerOf":
            result = node.fields.left ** node.fields.right
    ctx.fields.variables[node.fields.left] = result

def execute_iast(ctx: Context, node: AST_Assign(target=AST_Variable)):
    target = node.fields.target
    value = execute_iast(node.fields.value)
    ctx.fields.variables[target.concept_name] = value 

def execute_iast(ctx: Context, node: AST_FunctionDef):
    args = [arg for arg in node.fields.args]
    content = ["\n"+element for element in node.fields.body]
    exec(f"def {node.fields.name}({args}):{content}")