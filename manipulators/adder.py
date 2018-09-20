# adder.py

from math_tree import MathTreeManipulator, MathTreeNode

class Adder(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node):
        if node.data == '+':
            for i in range(len(node.child_list)):
                child_a = node.child_list[i]
                for j in range(i + 1, len(node.child_list)):
                    child_b = node.child_list[j]
                    if isinstance(child_a.data, float) and isinstance(child_b.data, float):
                        del node.child_list[j]
                        del node.child_list[i]
                        node.child_list.insert(0, MathTreeNode(child_a.data + child_b.data))
                        return node
            adjacent_swap_count = self._sort_list(node.child_list, lambda node: len(node.display_text()))
            if adjacent_swap_count > 0:
                return node