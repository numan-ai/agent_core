def execute_iast(ctx: Context, node: AST_Variable):
    return ctx.fields.variables[node.fields.value]


def execute_iast(ctx: Context, node: String):
    return node.fields.value


def execute_iast(ctx: Context, node: Number):
    return node.fields.value


def execute_iast(ctx: Context, node: AST_Attribute):
    return


def execute_iast(ctx: Context, node: AST_BinOp(op=AST_OpAdd)):
    return execute_iast(ctx, node.fields.left) + execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_BinOp(op=AST_OpSub)):
    return execute_iast(ctx, node.fields.left) - execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_BinOp(op=AST_OpMult)):
    return execute_iast(ctx, node.fields.left) * execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_BinOp(op=AST_OpDiv)):
    return execute_iast(ctx, node.fields.left) / execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_BinOp(op=AST_OpMod)):
    return execute_iast(ctx, node.fields.left) % execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_Compare(op=AST_OpGt)):
    return execute_iast(ctx, node.fields.left) > execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_Compare(op=AST_OpLt)):
    return execute_iast(ctx, node.fields.left) < execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_Compare(op=AST_OpEq)):
    return execute_iast(ctx, node.fields.left) == execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_Compare(op=AST_OpGtE)):
    return execute_iast(ctx, node.fields.left) >= execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_Compare(op=AST_OpLtE)):
    return execute_iast(ctx, node.fields.left) <= execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_Compare(op=AST_OpNotEq)):
    return execute_iast(ctx, node.fields.left) != execute_iast(ctx, node.fields.right)


def execute_iast(ctx: Context, node: AST_Assign(target=AST_Variable)):
    target = node.fields.target
    value = execute_iast(ctx, node.fields.value)
    ctx.fields.variables[target.fields.value] = value
    

def execute_iast(ctx: Context, node: AST_Call):
    callble = execute_iast(ctx, node.fields.func)
    args = []
    for arg in node.fields.args:
        args.append(execute_iast(ctx, arg))
        
    keyword_args = {}
    for keyword in node.fields.keywords:
        keyword_args[keyword.fields.arg] = execute_iast(ctx, keyword.fields.value)
        
    return call_with_kwargs(callble, args, keyword_args)


def execute_iast(ctx: Context, node: AST_If):
    if execute_iast(ctx, node.fields.test):
        for instruction in node.fields.body:
            execute_iast(ctx, instruction)
    else:
        for instruction in node.fields.orelse:
            execute_iast(ctx, instruction)
            
            
def execute_iast(ctx: Context, node: AST_For):
    for i in execute_iast(ctx, node.fields.iter):
        ctx.fields.variables[node.fields.target.fields.value] = i
        for instruction in node.fields.body:
            execute_iast(ctx, instruction)
            

def execute_iast(ctx: Context, node: AST_While):
    while execute_iast(ctx, node.fields.test):
        for instruction in node.fields.body:
            execute_iast(ctx, instruction)
            
    
def find_good_branch(node: AST_FunctionDef):
    for node in node.fields.body:
        if is_subconcept(node.get_concept().get_cid(), "AST_If"):
            print(node)
    return None


def main():
    ctx = Instance("Context", {
        "variables": {
            "print": print,
            "range": range,
        }
    })
    
    return find_good_branch(iast_code)
    
    for instruction in iast_code.fields.body:
        # print(instruction)
        execute_iast(ctx, instruction)
