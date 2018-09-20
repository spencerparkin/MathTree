# math_tree.py

import copy

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
    
    def advance_positions(self, lerp_value, eps=1e-5):
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

    def copy(self):
        return copy.deepcopy(self)
    
    @staticmethod
    def cast(obj):
        if isinstance(obj, MathTreeNode):
            return obj.copy()
        else:
            return MathTreeNode(obj)
    
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
    
    def __div__(self, other):
        return MathTreeNode('/', [self.copy(), self.cast(other)])
    
    def __rdiv__(self, other):
        return MathTreeNode('/', [self.cast(other), self.copy()])
    
    def __xor__(self, other):
        return MathTreeNode('^', [self.copy(), self.cast(other)])
    
    def __rxor__(self, other):
        return MathTreeNode('^', [self.cast(other), self.copy()])
    
    def __or__(self, other):
        return MathTreeNode('.', [self.copy(), self.cast(other)])
    
    def __ror__(self, other):
        return MathTreeNode('.', [self.cast(other), self.copy()])

class MathTreeManipulator(object):
    def __init__(self):
        pass

    def _manipulate_subtree(self, node):
        raise Exception('Method not implemented.')

    def manipulate_tree(self, node):
        new_node = self._manipulate_subtree(node)
        if new_node is not None:
            return new_node
        for i, child in enumerate(node.child_list):
            new_child = self.manipulate_tree(child)
            if new_child is not None:
                node.child_list[i] = new_node
                return node

def manipulate_tree(node, manipulator_list, max_iters=None):
    iter_count = 0
    expression_set = set()
    expression_set.add(node.expression_text())
    while max_iters is None or iter_count < max_iters:
        iter_count += 1
        for manipulator in manipulator_list:
            new_node = manipulator.manipulate_tree(node)
            if new_node is not None:
                node = new_node
                expression_text = node.expression_text()
                if expression_text in expression_set:
                    raise Exception('Expression repeated!')
                break
        else:
            break
    return node

def simplify_tree(node, max_iters=None):
    from manipulators.associator import Associator
    from manipulators.distributor import Distributor
    from manipulators.inverter import Inverter
    manipulator_list = [
        Associator(),
        Inverter(),
        Distributor()
    ]
    return manipulate_tree(node, manipulator_list, max_iters)