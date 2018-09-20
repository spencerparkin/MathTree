# script_edit.py

from PyQt5 import QtWidgets, QtCore, QtGui, Qsci

class ScriptEditPanel(QtWidgets.QDockWidget):
    execute_button_pressed_signal = QtCore.pyqtSignal(str)
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setWindowTitle('Script Editor')
        
        self.script_edit = ScriptEditControl(self)
        
        execute_button = QtWidgets.QPushButton('Execute')
        execute_button.clicked.connect(self.execute_button_pressed)
        
        load_button = QtWidgets.QPushButton('Load Script...')
        load_button.clicked.connect(self.load_button_pressed)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(execute_button)
        button_layout.addWidget(load_button)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.script_edit)
        main_layout.addLayout(button_layout)
        
        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(main_layout)
        
        self.setWidget(main_widget)
    
    def execute_button_pressed(self):
        code = self.script_edit.text()
        self.execute_button_pressed_signal.emit(code)

    def load_button_pressed(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Script')[0]
        if len(path) > 0:
            with open(path, 'r') as handle:
                code = handle.read()
            self.script_edit.setText(code)

class ScriptEditControl(Qsci.QsciScintilla):
    def __init__(self, parent):
        super ().__init__(parent)

        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        fontMetrics = QtGui.QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontMetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))

        self.markerDefine(Qsci.QsciScintilla.RightArrow, self.SC_MARK_MINUS)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"), self.SC_MARK_MINUS)

        self.setBraceMatching(Qsci.QsciScintilla.SloppyBraceMatch)

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))

        lexer = Qsci.QsciLexerPython()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)

        self.SendScintilla(Qsci.QsciScintilla.SCI_SETEOLMODE, Qsci.QsciScintilla.SC_EOL_CR)

        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        # TODO: Why is this never called?  :(
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        text_list = []
        for url in event.mimeData().urls():
            path = str(url.toLocalFile())
            with open(path, 'r') as handle:
                text_list.append(handle.read())
        self.setText('\n'.join(text_list))