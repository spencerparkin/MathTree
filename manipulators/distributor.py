# distribution.py

from math_tree import MathTreeManipulator, MathTreeNode

class Distributor(MathTreeManipulator):
    def __init__(self):
        super().__init__()
    
    def _manipulate_subtree(self, node_a):
        # TODO: We may not be able to indiscriminately distribute here.  Otherwise, we'll fight with collection.
        #       The general rule may be to never distribute anything of non-zero grade over a sum of zero grade.
        if any([product == node_a.data for product in ['.', '^', '*', 'rev']]):
            for i, node_b in enumerate(node_a.child_list):
                if node_b.data == '+' and len(node_b.child_list) > 1:
                    sum = MathTreeNode('+')
                    for node_c in node_b.child_list:
                        product = MathTreeNode(node_a.data)
                        product.child_list += [term.copy() for term in node_a.child_list[:i]]
                        product.child_list.append(node_c.copy())
                        product.child_list += [term.copy() for term in node_a.child_list[i+1:]]
                        sum.child_list.append(product)
                    return sum