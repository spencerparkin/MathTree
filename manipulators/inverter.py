# inverter.py

from math_tree import MathTreeManipulator, MathTreeNode

class Inverter(MathTreeManipulator):
    def __init__(self):
        super().__init__()

    def _manipulate_subtree(self, node):
        if node.data == '-' and len(node.child_list) == 2:
            return MathTreeNode('+', [
                node.child_list[0].copy(),
                MathTreeNode('*', [
                    MathTreeNode(-1.0),
                    MathTreeNode(node.child_list[1].copy())
                ])
            ])
        elif node.data == '/' and len(node.child_list) == 2:
            return MathTreeNode('*', [
                node.child_list[0].copy(),
                MathTreeNode('inv', [node.child_list[1].copy()])
            ])
        elif node.data == 'inv':
            pass
            # (abc)**{-1} = c**{-1}b**{-1}a**{-1}
            # a**{-1} = a/pow(mag(a),2.0)
            # What else can we do?  In general, finding inverses can boil down to inverting a matrix.
        elif node.data == 'rev':
            pass
            # rev(abc) = rev(c)rev(b)rev(a)