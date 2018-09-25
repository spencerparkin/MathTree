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
            if len(node_a.child_list) == 1:
                node_b = node_a.child_list[0]
                if node_b.data == '*' and len(node_b.child_list) > 1:
                    return MathTreeNode('*', [MathTreeNode(node_a.data, [node_c.copy()]) for node_c in reversed(node_b.child_list)])
                if node_a.data == 'inv':
                    if isinstance(node_b.data, float):
                        return MathTreeNode(1.0 / node_b.data)
                    scalar_list, vector_list = self._parse_blade(node_b)
                    if scalar_list is not None and vector_list is not None:
                        return MathTreeNode('*', [
                            MathTreeNode('inv', [
                                MathTreeNode('.', scalar_list + [
                                    MathTreeNode('*', [vector.copy() for vector in vector_list]),
                                    MathTreeNode('*', [vector.copy() for vector in vector_list])
                                ])
                            ]),
                            MathTreeNode('^', [vector.copy() for vector in reversed(vector_list)])
                        ])
                if node_a.data == 'rev':
                    grade = node_b.calculate_grade()
                    if grade == 0 or grade == 1:
                        return node_b