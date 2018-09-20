# inverter.py

from math_tree import MathTreeManipulator, MathTreeNode

class Inverter(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node_a):
        if node_a.data == '-' and len(node_a.child_list) == 2:
            return MathTreeNode('+', [
                node_a.child_list[0].copy(),
                MathTreeNode('*', [
                    MathTreeNode(-1.0),
                    node_a.child_list[1].copy()
                ])
            ])
        elif node_a.data == '/' and len(node_a.child_list) == 2:
            return MathTreeNode('*', [
                node_a.child_list[0].copy(),
                MathTreeNode('inv', [node_a.child_list[1].copy()])
            ])
        elif node_a.data == 'inv' or node_a.data == 'rev':
            for node_b in node_a.child_list:
                if node_b.data == '*' and len(node_b.child_list) > 1:
                    return MathTreeNode('*', [MathTreeNode(node_a.data, [node_c.copy()]) for node_c in reversed(node_b.child_list)])
            if node_a.data == 'inv':
                if len(node_a.child_list) == 1 and isinstance(node_a.child_list[0].data, float):
                    return MathTreeNode(1.0 / node_a.child_list[0].data)
            if node_a.data == 'rev':
                if len(node_a.child_list) == 1 and isinstance(node_a.child_list[0].data, float):
                    return node_a.child_list[0]
                # The reverse can be removed if we identify the sub-tree as a scalar or a vector.