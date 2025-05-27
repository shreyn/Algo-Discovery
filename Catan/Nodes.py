class ASTNode:
    def evaluate(self, context):
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()


class ConstantNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def evaluate(self, context):
        return self.value

    def __repr__(self):
        return str(self.value)


class VariableNode(ASTNode):
    def __init__(self, name):  # 'i', 'j', 'temp'
        self.name = name

    def evaluate(self, context):
        return context[self.name]

    def __repr__(self):
        return self.name


class ListGetNode(ASTNode):
    def __init__(self, index_expr):
        self.index_expr = index_expr  # Expr node that evaluates to an index

    def evaluate(self, context):
        idx = self.index_expr.evaluate(context)
        return context['L'][idx]

    def __repr__(self):
        return f"L[{self.index_expr}]"


class ListSetNode(ASTNode):
    def __init__(self, index_expr, value_expr):
        self.index_expr = index_expr
        self.value_expr = value_expr

    def evaluate(self, context):
        idx = self.index_expr.evaluate(context)
        val = self.value_expr.evaluate(context)
        context['L'][idx] = val
        return None

    def __repr__(self):
        return f"L[{self.index_expr}] = {self.value_expr}"


class SwapNode(ASTNode):
    def __init__(self, index1_expr, index2_expr):
        self.index1_expr = index1_expr
        self.index2_expr = index2_expr

    def evaluate(self, context):
        i = self.index1_expr.evaluate(context)
        j = self.index2_expr.evaluate(context)
        L = context['L']
        L[i], L[j] = L[j], L[i]

    def __repr__(self):
        return f"swap({self.index1_expr}, {self.index2_expr})"


class AssignNode(ASTNode):
    def __init__(self, var_node, expr):
        self.var_node = var_node  # VariableNode (e.g., 'i')
        self.expr = expr

    def evaluate(self, context):
        context[self.var_node.name] = self.expr.evaluate(context)

    def __repr__(self):
        return f"{self.var_node} = {self.expr}"


class BinOpNode(ASTNode):
    def __init__(self, op, left, right):
        self.op = op  # '+', '-', '>', etc.
        self.left = left
        self.right = right

    def evaluate(self, context):
        l = self.left.evaluate(context)
        r = self.right.evaluate(context)
        if self.op == '+':
            return l + r
        elif self.op == '-':
            return l - r
        elif self.op == '>':
            return l > r
        elif self.op == '<':
            return l < r
        elif self.op == '==':
            return l == r
        else:
            raise ValueError(f"Unsupported op: {self.op}")

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


class IfNode(ASTNode):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def evaluate(self, context):
        if self.condition.evaluate(context):
            self.then_branch.evaluate(context)
        else:
            self.else_branch.evaluate(context)

    def __repr__(self):
        return f"if ({self.condition}) {{ {self.then_branch} }} else {{ {self.else_branch} }}"


class LoopNode(ASTNode):
    def __init__(self, loop_var, limit_expr, body):
        self.loop_var = loop_var  # string like 'i' or 'j'
        self.limit_expr = limit_expr  # Expr
        self.body = body  # Stmt

    def evaluate(self, context):
        limit = self.limit_expr.evaluate(context)
        for val in range(limit):
            context[self.loop_var] = val
            self.body.evaluate(context)

    def __repr__(self):
        return f"for {self.loop_var} in range({self.limit_expr}): {{ {self.body} }}"



##### TESTING ####

# outer loop: for i in range(len(L)):
outer_loop = LoopNode(
    loop_var='i',
    limit_expr=ConstantNode(8),  # len(L), hardcoded to 3 for now
    body=LoopNode(
        loop_var='j',
        limit_expr=BinOpNode('-', ConstantNode(7), VariableNode('i')),  # len(L)-1 - i
        body=IfNode(
            condition=BinOpNode(
                '>',
                ListGetNode(VariableNode('j')),
                ListGetNode(BinOpNode('+', VariableNode('j'), ConstantNode(1)))
            ),
            then_branch=SwapNode(
                VariableNode('j'),
                BinOpNode('+', VariableNode('j'), ConstantNode(1))
            ),
            else_branch=AssignNode(VariableNode('temp'), ConstantNode(0))  # dummy else
        )
    )
)


context = {
    'L': [5, 2, 4, 8, 2, 1, 0, 6],
    'i': 0,
    'j': 0,
    'temp': 0
}

print("Program:")
print(outer_loop)

print("\nBefore:", context['L'])
outer_loop.evaluate(context)
print("After:", context['L'])
