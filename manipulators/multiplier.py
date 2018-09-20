# multiplier.py

from math_tree import MathTreeManipulator, MathTreeNode

class Multiplier(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node_a):
        if any([op == node_a.data for op in ['*', '.', '^']]):
            for i in range(len(node_a.child_list)):
                child_a = node_a.child_list[i]
                for j in range(i + 1, len(node_a.child_list)):
                    child_b = node_a.child_list[j]
                    if isinstance(child_a.data, float) and isinstance(child_b.data, float):
                        del node_a.child_list[j]
                        del node_a.child_list[i]
                        node_a.child_list.insert(0, MathTreeNode(child_a.data * child_b.data))
                        return node_a
            for node_b in node_a.child_list:
                if any([op == node_b.data for op in ['*', '.', '^']]):
                    for i, node_c in enumerate(node_b.child_list):
                        if isinstance(node_c.data, float) or (isinstance(node_c.data, str) and node_c.data[0] == '$'):
                            del node_b.child_list[i]
                            node_a.child_list.insert(0, node_c)
                            return node_a
            # TODO: Sort product where we can.  All products are commutative with respect to scalars.