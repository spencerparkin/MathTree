# window.py

from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math_tree import MathTreeNode
from math2d_aa_rect import AxisAlignedRectangle

class GLCanvas(QtOpenGL.QGLWidget):
    def __init__(self, parent):
        gl_format = QtOpenGL.QGLFormat()
        gl_format.setAlpha(True)
        gl_format.setDepth(False)
        gl_format.setDoubleBuffer(True)
        
        super().__init__(gl_format, parent)
        
        self.root_node = None
        
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.start(1)
        self.animation_timer.timeout.connect(self.animation_tick)
    
    def set_root_node(self, node):
        self.root_node = node
        if isinstance(node, MathTreeNode):
            node.calculate_target_positions()
            node.assign_initial_positions()
    
    def get_root_node(self):
        return self.root_node
     
    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 0.0)
    
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        
        if isinstance(self.root_node, MathTreeNode):
        
            viewport = glGetIntegerv(GL_VIEWPORT)
            viewport_rect = AxisAlignedRectangle()
            viewport_rect.min_point.x = 0.0
            viewport_rect.min_point.y = 0.0
            viewport_rect.max_point.x = float(viewport[2])
            viewport_rect.max_point.y = float(viewport[3])
        
            rect = self.root_node.calculate_subtree_bounding_rectangle(targets=True)
            rect.Scale(1.1)
            rect.ExpandToMatchAspectRatioOf(viewport_rect)
        
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(rect.min_point.x, rect.max_point.x, rect.min_point.y, rect.max_point.y)
            
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            glBegin(GL_LINES)
            try:
                glColor3f(0.0, 0.0, 0.0)
                self._render_edges(self.root_node)
            finally:
                glEnd()
            
            for node in self.root_node.yield_nodes():
                self._render_node(node)
        
        glFlush()
    
    def _render_node(self, node):
        rect = node.calculate_bounding_rectangle(targets=False)
        glBegin(GL_QUADS)
        try:
            glColor3f(0.8, 0.8, 0.8)
            glVertex2f(rect.min_point.x, rect.min_point.y)
            glVertex2f(rect.max_point.x, rect.min_point.y)
            glVertex2f(rect.max_point.x, rect.max_point.y)
            glVertex2f(rect.min_point.x, rect.max_point.y)
        finally:
            glEnd()

        glColor3f(0.0, 0.0, 0.0)
        self._render_text(GLUT_STROKE_ROMAN, node.display_text(), rect)

    def _render_text(self, font, text, rect):
        total_width = 0.0
        for char in text:
            width = glutStrokeWidth(font, ord(char))
            total_width += float(width)
        text_rect = AxisAlignedRectangle()
        text_rect.min_point.x = 0.0
        text_rect.max_point.x = total_width
        text_rect.min_point.y = 0.0
        text_rect.max_point.y = 119.05
        original_height = text_rect.Height()
        text_rect.ExpandToMatchAspectRatioOf(rect)
        height = text_rect.Height()
        scale = rect.Width() / text_rect.Width()
        glPushMatrix()
        try:
            glTranslatef(rect.min_point.x, rect.min_point.y + (height - original_height) * 0.5 * scale, 0.0)
            glScalef(scale, scale, 1.0)
            for char in text:
                glutStrokeCharacter(font, ord(char))
        finally:
            glPopMatrix()

    def _render_edges(self, node):
        for child in node.child_list:
            glVertex2f(node.position.x, node.position.y)
            glVertex2f(child.position.x, child.position.y)
            self._render_edges(child)

    def animation_tick(self):
        if isinstance(self.root_node, MathTreeNode):
            if not self.root_node.is_settled():
                self.root_node.advance_positions(0.05)
                self.update()
            else:
                pass # TODO: Apply tree manipulator somewhere.

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.locals_dict = {}
        
        self.setWindowTitle('Math Tree')

        self.canvas = GLCanvas(self)
        
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.returnPressed.connect(self.line_edit_enter_pressed)

        self.expression_label = QtWidgets.QLabel()
        self.expression_label.setFixedHeight(20)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.expression_label)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.line_edit)
        
        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
    
    def line_edit_enter_pressed(self):
        code = self.line_edit.text()
        
        from math_tree import MathTreeNode
        
        globals_dict = {
            '_n': lambda x: MathTreeNode(x),
            'inv': lambda x: MathTreeNode('inv', [x]),
            'rev': lambda x: MathTreeNode('rev', [x]),
            'e1': MathTreeNode('e1'),
            'e2': MathTreeNode('e2'),
            'e3': MathTreeNode('e3'),
            'no': MathTreeNode('no'),
            'ni': MathTreeNode('ni'),
            '_v': lambda x, y, z: MathTreeNode('+', [
                MathTreeNode('*', [MathTreeNode(x), MathTreeNode('e1')]),
                MathTreeNode('*', [MathTreeNode(y), MathTreeNode('e2')]),
                MathTreeNode('*', [MathTreeNode(z), MathTreeNode('e3')])
            ])
        }
        
        try:
            exec(code, globals_dict, self.locals_dict)
        except Exception as ex:
            error = str(ex)
            msgBox = QtWidgets.QMessageBox(parent=self)
            msgBox.setWindowTitle('Oops!')
            msgBox.setText('ERROR: ' + str(error))
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec_()
        else:
            self.line_edit.clear()
            root_node = self.locals_dict.get('root', None)
            self.canvas.set_root_node(root_node)
            self.canvas.update()
            text = '' if root_node is None else root_node.expression_text()
            metrics = QtGui.QFontMetrics(self.expression_label.font())
            text = metrics.elidedText(text, QtCore.Qt.ElideRight, self.expression_label.width())
            self.expression_label.setText(text)