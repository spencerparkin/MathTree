# outer_product_handler.py

from math_tree import MathTreeManipulator, MathTreeNode

class OuterProductHandler(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node):
        scalar_list, vector_list = self._parse_blade(node)
        if scalar_list is not None and vector_list is not None:
            adjacent_swap_count = self._sort_list(vector_list, sort_key=lambda vector: vector.data)
            if adjacent_swap_count > 0:
                new_node = MathTreeNode('^', scalar_list + vector_list)
                if adjacent_swap_count % 2 == 1:
                    new_node.child_list.insert(0, MathTreeNode(-1.0))
                return new_node