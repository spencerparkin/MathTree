# window.py

from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class GLCanvas(QtOpenGL.QGLWidget):
    def __init__(self, parent):
        gl_format = QtOpenGL.QGLFormat()
        gl_format.setAlpha(True)
        gl_format.setDepth(False)
        gl_format.setDoubleBuffer(True)
        
        super().__init__(gl_format, parent)
        
        self.root_node = None
        
    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 0.0)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        
        glColor3f(0.0, 0.0, 0.0)
        glWindowPos2f(10, 10)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('A'))
        
        glFlush()

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.locals_dict = {}
        
        self.setWindowTitle('Math Tree')

        self.canvas = GLCanvas(self)
        
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.returnPressed.connect(self.line_edit_enter_pressed)
        
        main_layout = QtWidgets.QVBoxLayout()
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
            self.canvas.root_node = self.locals_dict.get('root', None)