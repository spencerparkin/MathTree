# math_tree.py

import copy
import math

from math2d_vector import Vector
from math2d_aa_rect import AxisAlignedRectangle
from math2d_line_segment import LineSegment

class MathTreeNode(object):
    # Note that no node instance should appear more than once in the tree.
    
    def __init__(self, data, child_list=None):
        self.position = None
        self.target_position = None
        self.child_list = [] if child_list is None else child_list
        self.data = data

    def is_valid(self):
        node_set = set()
        for node in self.yield_nodes():
            key = str(node)
            if key in node_set:
                return False
            node_set.add(key)
        return True

    def size(self):
        return 1 + sum([child.size() for child in self.child_list])

    def calculate_target_positions(self):
        self.target_position = Vector(0.0, 0.0)
        
        for node in self.child_list:
            node.calculate_target_positions()
        
        rect_list = [node.calculate_subtree_bounding_rectangle(targets=True) for node in self.child_list]
        padding = 0.5
        total_width = sum([rect.Width() for rect in rect_list]) + float(len(rect_list) - 1) * padding
        
        position = Vector(-total_width / 2.0, -2.0)
        for i, node in enumerate(self.child_list):
            rect = rect_list[i]
            position += Vector(rect.Width() / 2.0, 0.0)
            node.translate_target_positions(position)
            position += Vector(rect.Width() / 2.0, 0.0)
            position += Vector(padding, 0.0)
    
    def calculate_subtree_bounding_rectangle(self, targets=True):
        rect = self.calculate_bounding_rectangle(targets)
        if len(self.child_list) > 0:
            for other_node in self.yield_nodes():
                rect.GrowFor(other_node.calculate_bounding_rectangle(targets))
        return rect
    
    def calculate_bounding_rectangle(self, targets=True):
        rect = AxisAlignedRectangle()
        rect.min_point = self.target_position if targets else self.position
        rect.max_point = self.target_position if targets else self.position
        rect.min_point -= Vector(0.5, 0.5)
        rect.max_point += Vector(0.5, 0.5)
        return rect
        
    def yield_nodes(self):
        yield self
        for child in self.child_list:
            yield from child.yield_nodes()
    
    def translate_target_positions(self, translation):
        self.target_position += translation
        for node in self.child_list:
            node.translate_target_positions(translation)
    
    def assign_initial_positions(self, parent_position=None):
        if parent_position is None:
            parent_position = Vector(0.0, 0.0)
        if self.position is None:
            self.position = parent_position
        for child in self.child_list:
            child.assign_initial_positions(self.position)
    
    def advance_positions(self, lerp_value, eps=1e-2):
        line_segment = LineSegment(self.position, self.target_position)
        if line_segment.Length() < eps:
            self.position = self.target_position
        else:
            self.position = line_segment.Lerp(lerp_value)
        for child in self.child_list:
            child.advance_positions(lerp_value)

    def is_settled(self):
        if self.position != self.target_position:
            return False
        for child in self.child_list:
            if not child.is_settled():
                return False
        return True

    def display_text(self):
        if isinstance(self.data, str):
            return self.data
        elif isinstance(self.data, float):
            return '%1.2f' % self.data
        else:
            return str(self.data)

    def expression_text(self):
        if len(self.child_list) > 0:
            display_text = self.display_text()
            if len(display_text) == 1:
                return '(' + display_text.join([child.expression_text() for child in self.child_list]) + ')'
            else:
                return display_text + '(' + ','.join([child.expression_text() for child in self.child_list]) + ')'
        else:
            return self.display_text()

    def generate_latex_code(self):
        pass

    def calculate_grade(self):
        if isinstance(self.data, float) or (isinstance(self.data, str) and self.data[0] == '$'):
            return 0
        elif isinstance(self.data, str) and self.data[0].isalpha() and len(self.child_list) == 0:
            return 1
        elif self.data == '+' or self.data == '^' or self.data == '.' or self.data == '*' or self.data == 'inv':
            if len(self.child_list) == 0:
                return 0
            grade_list = [child.calculate_grade() for child in self.child_list]
            if any([grade == None for grade in grade_list]):
                return None
            if len(grade_list) == 1:
                return grade_list[0]
            if self.data == '+':
                if all([grade_list[0] == grade for grade in grade_list[1:]]) or len(grade_list) == 1:
                    return grade_list[0]
            elif self.data == '^':
                return sum(grade_list)
            elif self.data == '.':
                non_zero_grade_list = [grade for grade in grade_list if grade != 0]
                if len(non_zero_grade_list) > 2:
                    raise Exception('Ambiguous inner product!')
                elif len(non_zero_grade_list) == 2:
                    grade_a = non_zero_grade_list[0]
                    grade_b = non_zero_grade_list[1]
                    return abs(grade_a - grade_b)
                elif len(non_zero_grade_list) == 1:
                    return non_zero_grade_list[0]
                else:
                    return 0

    def copy(self):
        return copy.deepcopy(self)
    
    @staticmethod
    def cast(obj):
        if isinstance(obj, MathTreeNode):
            return obj.copy()
        if isinstance(obj, float) or isinstance(obj, str):
            return MathTreeNode(obj)
        if isinstance(obj, int):
            return MathTreeNode(float(obj))
        raise Exception('Cannot cast: %s' % str(obj))
    
    def __add__(self, other):
        return MathTreeNode('+', [self.copy(), self.cast(other)])
    
    def __radd__(self, other):
        return MathTreeNode('+', [self.cast(other), self.copy()])
    
    def __sub__(self, other):
        return MathTreeNode('-', [self.copy(), self.cast(other)])
    
    def __rsub__(self, other):
        return MathTreeNode('-', [self.cast(other), self.copy()])
    
    def __mul__(self, other):
        return MathTreeNode('*', [self.copy(), self.cast(other)])

    def __rmul__(self, other):
        return MathTreeNode('*', [self.cast(other), self.copy()])
    
    def __truediv__(self, other):
        return MathTreeNode('/', [self.copy(), self.cast(other)])
    
    def __rtruediv__(self, other):
        return MathTreeNode('/', [self.cast(other), self.copy()])
    
    def __xor__(self, other):
        return MathTreeNode('^', [self.copy(), self.cast(other)])
    
    def __rxor__(self, other):
        return MathTreeNode('^', [self.cast(other), self.copy()])
    
    def __or__(self, other):
        return MathTreeNode('.', [self.copy(), self.cast(other)])
    
    def __ror__(self, other):
        return MathTreeNode('.', [self.cast(other), self.copy()])

    def is_perfect_join(self):
        if self.data[0].data != self.data[1].data:
            return False
        for child in self.child_list:
            if not child.is_perfect_join():
                return False
        return True

    def intersect_join(self):
        if self.data[0].data == self.data[1].data:
            new_node = MathTreeNode(self.data[0].data)
            for child in self.child_list:
                node = child.intersect_join()
                if node is not None:
                    new_node.child_list.append(node)
            return node

class MathTreeManipulator(object):
    def __init__(self):
        pass

    def _manipulate_subtree(self, node):
        raise Exception('Method not implemented.')

    def manipulate_tree(self, node):
        for i, child in enumerate(node.child_list):
            new_child = self.manipulate_tree(child)
            if new_child is not None:
                node.child_list[i] = new_child
                return node
        # Notice that we go as deep into the tree before we try to manipulate anything.
        # This is an optimization, because it lets us simplify sub-trees as far as possible
        # before they potentially get copied by distribution or something else that might
        # want to copy an entire sub-tree.
        new_node = self._manipulate_subtree(node)
        if new_node is not None:
            return new_node
    
    def _sort_list(self, given_list, sort_key):
        # Note that this is a stable sort.
        adjacent_swap_count = 0
        if len(given_list) > 1:
            keep_going = True
            while keep_going:
                keep_going = False
                for i in range(len(given_list) - 1):
                    key_a = sort_key(given_list[i])
                    key_b = sort_key(given_list[i + 1])
                    if key_a > key_b:
                        given_list[i], given_list[i + 1] = given_list[i + 1], given_list[i]
                        adjacent_swap_count += 1
                        keep_going = True
        return adjacent_swap_count
    
    def _bucket_sort(self, node):
        scalar_list = []
        vector_list = []
        other_list = []
        for child in node.child_list:
            grade = child.calculate_grade()
            if grade == 0:
                scalar_list.append(child)
            elif grade == 1:
                vector_list.append(child)
            else:
                other_list.append(child)
        return scalar_list, vector_list, other_list

    def _parse_blade(self, node):
        if any([op == node.data for op in ['.', '^', '*']]):
            scalar_list, vector_list, other_list = self._bucket_sort(node)
            if len(other_list) > 0:
                return None, None
            if len(vector_list) > 1 and node.data != '^':
                return None, None
            return scalar_list, vector_list
        else:
            grade = node.calculate_grade()
            if grade == 0:
                return [node], []
            if grade == 1:
                return [], [node]
        return None, None

    def _join_trees(self, root_a, root_b):
        # This might not be the best way to join the trees, but I like the general idea.
        root = MathTreeNode((root_a, root_b))
        queue = [root]
        while len(queue) > 0:
            parent = queue.pop(0)
            child_list_a = parent.data[0].child_list
            child_list_b = parent.data[1].child_list
            i = 0
            j = 0
            while True:
                if i < len(child_list_a) and j < len(child_list_b):
                    child_a = child_list_a[i]
                    child_b = child_list_b[j]
                    if child_a.data == child_b.data:
                        parent.child_list.append(MathTreeNode((child_a, child_b)))
                        queue.append(parent.child_list[-1])
                    else:
                        u = i
                        while u < len(child_list_a) and child_list_a[u].data != child_b.data:
                            u += 1
                        v = j
                        while j < len(child_list_b) and child_list_b[v].data != child_a.data:
                            v += 1
                        if u <= v:
                            while i < u:
                                parent.child_list.append(MathTreeNode((child_list_a[i], None)))
                                i += 1
                        elif v < u:
                            while j < v:
                                parent.child_list.append(MathTreeNode((None, child_list_b[i])))
                                j += 1
                elif i < len(child_list_a):
                    while i < len(child_list_a):
                        parent.child_list.append(MathTreeNode((child_list_a[i], None)))
                        i += 1
                elif j < len(child_list_b):
                    while j < len(child_list_b):
                        parent.child_list.append(MathTreeNode((None, child_list_b[j])))
                        j += 1
                else:
                    break
        return root

def manipulate_tree(node, manipulator_list, max_iters=None, max_tree_size=None, log=print):
    iter_count = 0
    expression_set = set()
    expression_set.add(node.expression_text())
    while max_iters is None or iter_count < max_iters:
        iter_count += 1
        for manipulator in manipulator_list:
            new_node = manipulator.manipulate_tree(node)
            if new_node is not None:
                log(manipulator.__class__.__name__)
                if not new_node.is_valid():
                    raise Exception('Manipulated tree is not valid!')
                tree_size = new_node.size()
                log('Tree size: %d' % tree_size)
                if max_tree_size is not None:
                    if tree_size > max_tree_size:
                        raise Exception('Tree size (%d) exceeded limit (%d).' % (tree_size, max_tree_size))
                node = new_node
                expression_text = node.expression_text()
                if expression_text in expression_set:
                    raise Exception('Expression repeated!')
                expression_set.add(expression_text)
                break
        else:
            break
    return node

# I believe it worth noting here an alternative to the entire approach taken in this program to the
# simplifying of a general GA expression.  Forgetting about a free-form tree, create a data-structure
# that gives the general layout of any fully simplified GA expression: a sum over blades, each blade
# being a polynomial paired with an ordered set of vectors.  Now all that remains is the ability to
# combine any two of these data-structure together into another such data-structure in any operation.
# Admittedly, this was my original approach in previous programs, and it worked very well for numeric
# computation, and I believe it could also work for symbolic computation as well.  So why might a free-form
# tree, and the approach taken in this program, be any better?  I struggle with this question.  Maybe it's
# not any better.  Maybe it's worse.  One idea, however, is that there is more flexibility in a free-form
# tree if there were ever other forms of the expression that we wanted to find.  For example, we might
# want the factored form of a simplified GA expression in terms of the inner product.  I as yet have no
# idea how to provide this functionality, but our choice of data-structure does not limit us to only GA
# expressions of the most expanded, simplified form.
def simplify_tree(node, max_iters=None, bilinear_form=None, log=print):
    from manipulators.adder import Adder
    from manipulators.associator import Associator
    from manipulators.degenerate_case_handler import DegenerateCaseHandler
    from manipulators.distributor import Distributor
    from manipulators.geometric_product_handler import GeometricProductHandler
    from manipulators.inner_product_handler import InnerProductHandler
    from manipulators.inverter import Inverter
    from manipulators.multiplier import Multiplier
    from manipulators.outer_product_handler import OuterProductHandler
    # The order of manipulators here has been carefully chosen.
    # In some cases, the order may not matter; in others, very much so.
    manipulator_list = [
        InnerProductHandler(bilinear_form),
        Associator(),
        DegenerateCaseHandler(),
        Inverter(),
        GeometricProductHandler(),
        Adder(),
        Multiplier(),
        OuterProductHandler(),
        Distributor(),
    ]
    return manipulate_tree(node, manipulator_list, max_iters, log=log)