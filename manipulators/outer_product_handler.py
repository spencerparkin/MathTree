# outer_product_handler.py

from math_tree import MathTreeManipulator, MathTreeNode

class OuterProductHandler(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node):
        scalar_list, vector_list = self._parse_blade(node)
        if scalar_list is not None and vector_list is not None:
            for i in range(len(vector_list)):
                vector_a = vector_list[i]
                for j in range(i + 1, len(vector_list)):
                    vector_b = vector_list[j]
                    if vector_a.data == vector_b.data:
                        return MathTreeNode(0.0)
            adjacent_swap_count = self._sort_list(vector_list, sort_key=lambda vector: vector.data)
            if adjacent_swap_count > 0:
                new_node = MathTreeNode('^', scalar_list + vector_list)
                if adjacent_swap_count % 2 == 1:
                    new_node.child_list.insert(0, MathTreeNode(-1.0))
                return new_node