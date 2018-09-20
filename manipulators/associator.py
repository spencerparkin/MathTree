# associator.py

from math_tree import MathTreeManipulator, MathTreeNode

class Associator(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node_a):
        # Note that the inner product and subtraction are not generally associative.
        if any([op == node_a.data for op in ['+', '*', '^']]):
            for i, node_b in enumerate(node_a.child_list):
                if node_b.data == node_a.data:
                    node = MathTreeNode(node_a.data)
                    node.child_list += [node_c.copy() for node_c in node_a.child_list[:i]]
                    node.child_list += [node_c.copy() for node_c in node_b.child_list]
                    node.child_list += [node_c.copy() for node_c in node_a.child_list[i+1:]]
                    return node