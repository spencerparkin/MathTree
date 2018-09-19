# main.py

import sys
import traceback

sys.path.append(r'C:\dev\pyMath2D')
sys.path.append(r'C:\dev\MathTree')

from PyQt5 import QtGui, QtWidgets
from OpenGL.GLUT import *

def exception_hook(cls, exc, tb):
    sys.__excepthook__(cls, exc, tb)

if __name__ == '__main__':
    sys.excepthook = exception_hook
    
    try:
        glutInit(sys.argv)
        
        app = QtWidgets.QApplication(sys.argv)
        
        from window import Window
        
        win = Window()
        win.resize(640, 480)
        win.show()
        
        sys.exit(app.exec_())
        
    except Exception as ex:
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
        error = str(ex)
        print('ERROR:' + error)