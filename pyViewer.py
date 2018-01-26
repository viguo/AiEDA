import sys
from PyQt5.QtWidgets import (QWidget, QMessageBox, QApplication, QDesktopWidget,QMainWindow,
                             QAction,qApp,QMenu,QTextEdit,QLineEdit,QGridLayout,QApplication,QLabel)
from PyQt5.QtGui import QIcon

class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        exitAct = QAction(QIcon('spyder.png'), '&Exit', self)
        exitAct.setShortcut("Ctrl+Q")
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        openAct = QAction("Open", self)
        openAct.setShortcut("Ctrl+O")
        openAct.setStatusTip('Open File')
        openAct.setStatusTip("Open file")

        ####QMenu
        impMenu = QMenu("Import",self)
        impMenu.addAction(exitAct)

        ## check
        viewStatAct = QAction("View Statusbar", self,checkable=True)
        viewStatAct.setStatusTip("View Statusbar")
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.toggleMenu)

        menubar = self.menuBar()
        ## define actions
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        fileMenu.addAction(openAct)
        fileMenu.addMenu(impMenu)
        fileMenu.addAction(viewStatAct)

        editMenu = menubar.addMenu('&Edit')

        #self.resize(250,150)
        self.center()
        #self.textEditor()

        self.setWindowTitle('defViewer')
        self.statusBar().showMessage("ready")
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        #print(type(cp), type(qr))
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        textEdit  = QTextEdit()
        self.setCentralWidget(textEdit)
    def textEditor(self):
        title = QLabel('Tile')
        author = QLabel('Author')
        review = QLabel('Review')

        tileEdit = QLineEdit()
        authorEdit = QLineEdit()
        reviewEdit = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title,1,0)
        grid.addWidget(tileEdit,1,1)

        grid.addWidget(author,2,0)
        grid.addWidget(authorEdit,2,1)

        grid.addWidget(review,3,0)
        grid.addWidget(reviewEdit,3,1,5,1)

        self.setLayout(grid)

        self.setGeometry(300,300,350,300)
        self.setWindowTitle("Review")




    def toggleMenu(self,state):
        if True:
            self.statusbar.show()
        else:
            self.statusbar.hide()
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())