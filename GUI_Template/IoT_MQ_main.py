import os
import sys
import PyQt5
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from gui_helpers import *

import time
import datetime

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)        

        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 100, 800, 600)
        self.setWindowTitle('White Cubes GUI')        

        # Init QDockWidget objects placed in gui_helpers
        self.Connection = ConnectionDock()
        self.Publish = PublishDock()
        self.Subscriptions = SubscriptionsDock()
        self.Messages = MessagesDock()
       
        # align to area 
        self.addDockWidget(Qt.TopDockWidgetArea, self.Connection)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.Publish)
        self.addDockWidget(Qt.RightDockWidgetArea, self.Subscriptions)        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.Messages)
    

app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
