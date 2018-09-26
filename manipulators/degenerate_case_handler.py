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
        op_list = ['*', '^']
        for i in range(2):
            if node.data == op_list[i]:
                for j, child in enumerate(node.child_list):
                    if child.data == op_list[(i + 1) % 2]:
                        for k in range(len(node.child_list)):
                            if k != j:
                                if node.child_list[k].calculate_grade() != 0:
                                    break
                        else:
                            node.data = op_list[(i + 1) % 2]
                            return node
                        break