# collector.py

from math_tree import MathTreeManipulator, MathTreeNode

class Collector(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node):
        # TODO: We may not be able to indiscriminately collect here.  Otherwise, we'll fight with distribution.
        if node.data == '+':
            for i in range(len(node.child_list)):
                child_a = node.child_list[i]
                for j in range(i + 1, len(node.child_list)):
                    child_b = node.child_list[j]
                    if child_a.data == child_b.data and any([op == child_a.data for op in ['^', '.', '*']]):
                        joined_root = self._join_trees(child_a, child_b)
                        product_a = MathTreeNode('*', [])
                        product_b = MathTreeNode('*', [])
                        for joined_child in joined_root.child_list:
                            if joined_child.data[0] is None and joined_child.data[1].calculate_grade() == 0:
                                product_a.child_list.append(joined_child.data[1])
                            elif joined_child.data[1] is None and joined_child.data[0].calculate_grade() == 0:
                                product_b.child_list.append(joined_child.data[0])
                            elif not joined_child.is_perfect_join():
                                break
                        else:
                            del node.child_list[j]
                            del node.child_list[i]
                            node.child_list.append(MathTreeNode('*', [
                                MathTreeNode('+', [
                                    product_a,
                                    product_b
                                ]),
                                joined_root.intersect_join()
                            ]))
                            return self