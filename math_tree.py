# math_tree.py

import copy

from math2d_vector import Vector
from math2d_aa_rect import AxisAlignedRectangle
from math2d_line_segment import LineSegment

class MathTreeNode(object):
    def __init__(self, data, child_list=None):
        self.position = None
        self.target_position = None
        self.child_list = [] if child_list is None else child_list
        self.data = data
    
    def calculate_target_position(self):
        self.target_position = Vector(0.0, 0.0)
        
        for node in self.child_list:
            node.calculate_target_position()
        
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