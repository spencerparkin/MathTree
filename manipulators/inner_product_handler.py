# inner_product_handler.py

from math_tree import MathTreeManipulator, MathTreeNode

class InnerProductHandler(MathTreeManipulator):
    def __init__(self, bilinear_form=None):
        super().__init__()
        self.bilinear_form = bilinear_form if bilinear_form is not None else self._default_bilinear_form

    def _manipulate_subtree(self, node):
        if node.data == '.':
            scalar_list_a = scalar_list_b = None
            vector_list_a = vector_list_b = None
            other_list = []
            for child in node.child_list:
                scalar_list, vector_list = self._parse_blade(child)
                if scalar_list is not None and vector_list is not None and len(vector_list) > 0:
                    if scalar_list_a is None:
                        scalar_list_a = scalar_list
                        vector_list_a = vector_list
                    elif scalar_list_b is None:
                        scalar_list_b = scalar_list
                        vector_list_b = vector_list
                    else:
                        raise Exception('Ambiguous inner product!')
                else:
                    other_list.append(child)
            if scalar_list_a is not None and scalar_list_b is not None:
                if len(vector_list_a) == 1 and len(vector_list_b) == 1:
                    vector_a = vector_list_a[0].data
                    vector_b = vector_list_b[0].data
                    scalar = self.bilinear_form(vector_a, vector_b)
                    if scalar is not None:
                        return MathTreeNode('*', [MathTreeNode(scalar)] + other_list + scalar_list_a + scalar_list_b)
                    elif vector_a > vector_b:
                        return MathTreeNode('.', other_list + scalar_list_a + scalar_list_b + vector_list_b + vector_list_a)
                elif len(vector_list_a) == 1 and len(vector_list_b) > 1:
                    sum = self._expand_vector_with_blade(vector_list_a[0], vector_list_b, 1)
                    return MathTreeNode('*', other_list + scalar_list_a + scalar_list_b + [sum])
                elif len(vector_list_a) > 1 and len(vector_list_b) == 1:
                    j = 1 if len(vector_list_a) % 2 == 1 else 0
                    sum = self._expand_vector_with_blade(vector_list_b[0], vector_list_a, j)
                    return MathTreeNode('*', other_list + scalar_list_a + scalar_list_b + [sum])
                elif len(vector_list_a) > 1 and len(vector_list_b) > 1:
                    product = MathTreeNode('*')
                    product.child_list += other_list + scalar_list_a + scalar_list_b
                    if len(vector_list_a) >= len(vector_list_b):
                        vector = vector_list_a[-1]
                        del vector_list_a[-1]
                        product.child_list.append(MathTreeNode('.', [
                            MathTreeNode('^', vector_list_a),
                            MathTreeNode('.', [
                                vector,
                                MathTreeNode('^', vector_list_b)
                            ])
                        ]))
                    else:
                        vector = vector_list_b[0]
                        del vector_list_b[0]
                        product.child_list.append(MathTreeNode('.', [
                            MathTreeNode('.', [
                                MathTreeNode('^', vector_list_a),
                                vector
                            ]),
                            MathTreeNode('^', vector_list_b)
                        ]))
                    return product

    def _expand_vector_with_blade(self, vector, vector_list, j):
        sum = MathTreeNode('+')
        for i in range(len(vector_list)):
            product = MathTreeNode('.')
            if i % 2 == j:
                product.child_list.append(MathTreeNode(-1.0))
            product.child_list += [vector.copy(), vector_list[i].copy()]
            blade = MathTreeNode('^')
            blade.child_list.append(product)
            blade.child_list += [vec.copy() for vec in vector_list[:i]]
            blade.child_list += [vec.copy() for vec in vector_list[i + 1:]]
            sum.child_list.append(blade)
        return sum

    def _default_bilinear_form(self, vector_a, vector_b):
        key = vector_a + '.' + vector_b
        if key in _conformal_bilinear_form_map:
            return _conformal_bilinear_form_map[key]
        if (vector_a == 'no' or vector_a == 'ni') and vector_b[0] == 'e':
            return 0.0
        if (vector_b == 'no' or vector_b == 'ni') and vector_a[0] == 'e':
            return 0.0

_conformal_bilinear_form_map = {
    'e1.e1': 1.0,
    'e1.e2': 0.0,
    'e1.e3': 0.0,
    'e1.no': 0.0,
    'e1.ni': 0.0,

    'e2.e1': 0.0,
    'e2.e2': 1.0,
    'e2.e3': 0.0,
    'e2.no': 0.0,
    'e2.ni': 0.0,

    'e3.e1': 0.0,
    'e3.e2': 0.0,
    'e3.e3': 1.0,
    'e3.no': 0.0,
    'e3.ni': 0.0,

    'no.e1': 0.0,
    'no.e2': 0.0,
    'no.e3': 0.0,
    'no.no': 0.0,
    'no.ni': -1.0,

    'ni.e1': 0.0,
    'ni.e2': 0.0,
    'ni.e3': 0.0,
    'ni.no': -1.0,
    'ni.ni': 0.0
}