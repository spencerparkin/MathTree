# degenerate_case_handler.py

from math_tree import MathTreeManipulator, MathTreeNode

class DegenerateCaseHandler(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node):
        if any([op == node.data for op in ['*', '.', '^', '+']]):
            if len(node.child_list) == 1:
                return node.child_list[0]
        if any([op == node.data for op in ['*', '.', '^']]):
            if len(node.child_list) == 0:
                return MathTreeNode(1.0)
            if any([child.data == 0.0 for child in node.child_list]):
                return MathTreeNode(0.0)
            for i, child in enumerate(node.child_list):
                if child.data == 1.0:
                    del node.child_list[i]
                    return node
        if node.data == '+':
            if len(node.child_list) == 0:
                return MathTreeNode(0.0)
            for i, child in enumerate(node.child_list):
                if child.data == 0.0:
                    del node.child_list[i]
                    return node