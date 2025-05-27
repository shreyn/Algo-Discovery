import random
from Nodes import ConstantNode, VariableNode, ListGetNode, ListSetNode, SwapNode, AssignNode, BinOpNode, IfNode, LoopNode

def p_leaf_at_depth(current_depth, max_depth):
    return 1.0 if current_depth >= max_depth else 0.05 + 0.5 * (current_depth / max_depth)

def generate_random_tree(max_depth, variables, current_depth=0, return_type='Stmt'):
    def force_variable():
        return VariableNode(random.choice(variables))

    p_leaf = p_leaf_at_depth(current_depth, max_depth)

    # Terminal node
    if random.random() < p_leaf:
        if return_type == 'Expr':
            if random.random() < 0.4:
                return ConstantNode(random.randint(0, 10))
            elif random.random() < 0.7:
                return force_variable()
            else:
                return ListGetNode(force_variable())  # L[i]
        elif return_type == 'Bool':
            left = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
            right = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
            return BinOpNode('>', left, right)
        elif return_type == 'Stmt':
            var = force_variable()
            val = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
            return AssignNode(var, val)

    # Non-terminal node
    if return_type == 'Expr':
        op = random.choice(['+', '-'])
        left = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
        right = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
        return BinOpNode(op, left, right)

    elif return_type == 'Bool':
        op = random.choice(['>', '<', '=='])
        left = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
        right = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
        return BinOpNode(op, left, right)

    elif return_type == 'Stmt':
        op = random.choice(['assign', 'set', 'swap', 'if', 'loop'])

        if op == 'assign':
            var = force_variable()
            val = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
            return AssignNode(var, val)

        elif op == 'set':
            index = force_variable()
            val = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
            return ListSetNode(index, val)

        elif op == 'swap':
            i1 = force_variable()
            i2 = force_variable()
            return SwapNode(i1, i2)

        elif op == 'if':
            cond = generate_random_tree(max_depth, variables, current_depth + 1, 'Bool')
            then_branch = generate_random_tree(max_depth, variables, current_depth + 1, 'Stmt')
            else_branch = generate_random_tree(max_depth, variables, current_depth + 1, 'Stmt')
            return IfNode(cond, then_branch, else_branch)
        elif op == 'loop':
            loop_var = random.choice(variables)
            limit = generate_random_tree(max_depth, variables, current_depth + 1, 'Expr')
            body = generate_random_tree(max_depth, variables, current_depth + 1, 'Stmt')
            return LoopNode(loop_var, limit, body)


    raise ValueError(f"Unsupported return type: {return_type}")


variables = ['i', 'j']
context = {
    'L': [5, 3, 1],
    'i': 0,
    'j': 1,
    'temp': 0
}

tree = generate_random_tree(max_depth=4, variables=variables)
print("Generated Program:")
print(tree)

print("\nBefore Execution:", context['L'])
tree.evaluate(context)
print("After Execution:", context['L'])
