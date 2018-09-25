# geometric_product_handler.py

from math_tree import MathTreeManipulator, MathTreeNode

class GeometricProductHandler(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node):
        new_node = self._manipulate_subtree_internal(node, False)
        if new_node:
            return new_node
        return self._manipulate_subtree_internal(node, True)
        
    def _manipulate_subtree_internal(self, node, allow_same_grade):
        if node.data == '*':
            for i in range(len(node.child_list) - 1):
                node_a = node.child_list[i]
                node_b = node.child_list[i + 1]
                scalar_list_a, vector_list_a = self._parse_blade(node_a)
                scalar_list_b, vector_list_b = self._parse_blade(node_b)
                if vector_list_a is not None and vector_list_b is not None:
                    if len(vector_list_a) > 0 and len(vector_list_b) > 0:
                        if len(vector_list_a) != len(vector_list_b) or allow_same_grade:
                            if len(vector_list_a) == 1 or len(vector_list_b) == 1:
                                sum = MathTreeNode('+', [
                                    MathTreeNode('.', [
                                        MathTreeNode('^', [vector.copy() for vector in vector_list_a]),
                                        MathTreeNode('^', [vector.copy() for vector in vector_list_b])
                                    ]),
                                    MathTreeNode('^', [
                                        MathTreeNode('^', [vector.copy() for vector in vector_list_a]),
                                        MathTreeNode('^', [vector.copy() for vector in vector_list_b])
                                    ]),
                                ])
                            else:
                                if len(vector_list_a) <= len(vector_list_b):
                                    sum = MathTreeNode('+', [
                                        MathTreeNode('*', [
                                            vector_list_a[0].copy(),
                                            MathTreeNode('^', [vector.copy() for vector in vector_list_a[1:]]),
                                            MathTreeNode('^', [vector.copy() for vector in vector_list_b])
                                        ]),
                                        MathTreeNode('*', [
                                            MathTreeNode(-1.0),
                                            MathTreeNode('.', [
                                                vector_list_a[0].copy(),
                                                MathTreeNode('^', [vector.copy() for vector in vector_list_a[1:]]),
                                            ]),
                                            MathTreeNode('^', [vector.copy() for vector in vector_list_b])
                                        ])
                                    ])
                                else:
                                    sum = MathTreeNode('+', [
                                        MathTreeNode('*', [
                                            MathTreeNode('^', [vector.copy() for vector in vector_list_a]),
                                            MathTreeNode('^', [vector.copy() for vector in vector_list_b[:-1]]),
                                            vector_list_b[-1].copy()
                                        ]),
                                        MathTreeNode('*', [
                                            MathTreeNode(-1.0),
                                            MathTreeNode('^', [vector.copy() for vector in vector_list_a]),
                                            MathTreeNode('.', [
                                                MathTreeNode('^', [vector.copy() for vector in vector_list_b[:-1]]),
                                                vector_list_b[-1].copy()
                                            ])
                                        ])
                                    ])
                            node.child_list += scalar_list_a + scalar_list_b
                            del node.child_list[i]
                            del node.child_list[i]
                            node.child_list.insert(i, sum)
                            return node