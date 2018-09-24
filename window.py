# window.py

import traceback

from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math_tree import MathTreeNode, simplify_tree
from math2d_aa_rect import AxisAlignedRectangle
from math2d_line_segment import LineSegment
from math2d_vector import Vector
from script_edit import ScriptEditPanel

class GLCanvas(QtOpenGL.QGLWidget):
    simplify_step_taken_signal = QtCore.pyqtSignal()
    
    def __init__(self, parent):
        gl_format = QtOpenGL.QGLFormat()
        gl_format.setAlpha(True)
        gl_format.setDepth(False)
        gl_format.setDoubleBuffer(True)
        
        super().__init__(gl_format, parent)
        
        self.root_node = None
        self.proj_rect = None
        self.anim_proj_rect = AxisAlignedRectangle()
        
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.start(1)
        self.animation_timer.timeout.connect(self.animation_tick)
        
        self.auto_simplify = False

        self.dragPos = None
        self.dragging = False
    
    def set_root_node(self, node):
        self.root_node = node
        if isinstance(node, MathTreeNode):
            node.calculate_target_positions()
            node.assign_initial_positions()
            self._recalc_projection_rect()
    
    def get_root_node(self):
        return self.root_node
     
    def mousePressEvent(self, event):
         if event.button() == QtCore.Qt.LeftButton:
             self.grabMouse()
             self.dragPos = event.pos()
             self.dragging = True
         elif event.button() == QtCore.Qt.RightButton:
             pass  # TODO: Maybe use OpenGL selection mechanism on the tree?

    def mouseMoveEvent(self, event):
        if self.dragging:
            sensativity = 0.005 * self.proj_rect.Width()
            delta = event.pos() - self.dragPos
            delta = Vector(-float(delta.x()), float(delta.y())) * sensativity
            self.dragPos = event.pos()
            self.proj_rect.min_point += delta
            self.proj_rect.max_point += delta
            self.update()

    def mouseReleaseEvent(self, event):
        self.releaseMouse()
        self.dragging = False

    def wheelEvent(self, event):
        delta = int(event.angleDelta().y() / 120)
        if delta < 0.0:
            scale = 1.1
        else:
            scale = 0.9
        delta = abs(delta)
        for i in range(delta):
            self.proj_rect.Scale(scale)
        self.update()

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 0.0)
    
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        if isinstance(self.root_node, MathTreeNode):
            self._recalc_projection_rect()

    def _recalc_projection_rect(self):

        viewport = glGetIntegerv(GL_VIEWPORT)
        viewport_rect = AxisAlignedRectangle()
        viewport_rect.min_point.x = 0.0
        viewport_rect.min_point.y = 0.0
        viewport_rect.max_point.x = float(viewport[2])
        viewport_rect.max_point.y = float(viewport[3])

        self.proj_rect = self.root_node.calculate_subtree_bounding_rectangle(targets=True)
        self.proj_rect.Scale(1.1)
        self.proj_rect.ExpandToMatchAspectRatioOf(viewport_rect)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        
        if isinstance(self.root_node, MathTreeNode):

            if self.proj_rect is None:
                self._recalc_projection_rect()

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(
                self.anim_proj_rect.min_point.x,
                self.anim_proj_rect.max_point.x,
                self.anim_proj_rect.min_point.y,
                self.anim_proj_rect.max_point.y)
            
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
            elif self.auto_simplify:
                self.do_simplify_step()
        if self.proj_rect is not None:
            if ((self.anim_proj_rect.min_point - self.proj_rect.min_point).Length() > 0.0 or
                (self.anim_proj_rect.max_point - self.proj_rect.max_point).Length() > 0.0):
                self.anim_proj_rect.min_point = LineSegment(self.anim_proj_rect.min_point, self.proj_rect.min_point).Lerp(0.1)
                self.anim_proj_rect.max_point = LineSegment(self.anim_proj_rect.max_point, self.proj_rect.max_point).Lerp(0.1)
                self.update()
    
    def do_simplify_step(self):
        if isinstance(self.root_node, MathTreeNode):
            try:
                new_root_node = simplify_tree(self.root_node, max_iters=1)
            except Exception as ex:
                tb = traceback.format_exc()
                error = str(ex)
                msgBox = QtWidgets.QMessageBox(parent=self)
                msgBox.setWindowTitle('Simplification error!')
                msgBox.setText('ERROR: ' + str(error) + '\n\n' + tb)
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msgBox.exec_()
                self.auto_simplify = False
            else:
                self.root_node = new_root_node
                self.root_node.calculate_target_positions()
                self.root_node.assign_initial_positions()
                self.update()
                self.simplify_step_taken_signal.emit()

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.locals_dict = {}
        
        self.setWindowTitle('Math Tree')

        self.canvas = GLCanvas(self)
        self.canvas.simplify_step_taken_signal.connect(self.simplify_step_taken)
        
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.returnPressed.connect(self.line_edit_enter_pressed)

        self.expression_label = QtWidgets.QLabel()
        self.expression_label.setFixedHeight(20)
        
        simplify_button = QtWidgets.QPushButton('Simplify')
        simplify_button.setFixedWidth(60)
        simplify_button.clicked.connect(self.simplify_button_pressed)
        
        self.auto_simplify_check = QtWidgets.QCheckBox('Auto Simplify')
        self.auto_simplify_check.clicked.connect(self.auto_simplify_check_pressed)
        self.auto_simplify_check.setFixedWidth(80)
        
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(simplify_button)
        top_layout.addWidget(self.expression_label)
        top_layout.addWidget(self.auto_simplify_check)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.line_edit)
        
        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
        
        script_edit_panel = ScriptEditPanel(self)
        script_edit_panel.execute_button_pressed_signal.connect(self.script_edit_execute_pressed)
        
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, script_edit_panel)
    
    def auto_simplify_check_pressed(self):
        self.canvas.auto_simplify = self.auto_simplify_check.isChecked()
    
    def script_edit_execute_pressed(self, code):
        self._execute_code(code)
    
    def line_edit_enter_pressed(self):
        code = self.line_edit.text()
        if self._execute_code(code):
            self.line_edit.clear()
    
    def _execute_code(self, code):
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
            ]),
            'simplify': simplify_tree
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
            return False
        else:
            root_node = self.locals_dict.get('root', None)
            self.canvas.set_root_node(root_node)
            self.canvas.update()
            self.update_expression_label()
            return True
    
    def update_expression_label(self):
        root_node = self.canvas.get_root_node()
        text = '' if root_node is None else root_node.expression_text()
        metrics = QtGui.QFontMetrics(self.expression_label.font())
        text = metrics.elidedText(text, QtCore.Qt.ElideRight, self.expression_label.width())
        self.expression_label.setText(text)
    
    def simplify_step_taken(self):
        self.update_expression_label()
    
    def simplify_button_pressed(self):
        self.canvas.do_simplify_step()
            