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
        self.setGeometry(30, 100, 600, 600)
        self.setWindowTitle('White Cubes GUI')        

        # Init QDockWidget objects placed in gui_helpers
        self.main_settings = MainSettingsDock()
        self.settings = SettingsDock()
        self.main = MainDock()
       
        # align to area 
        self.addDockWidget(Qt.RightDockWidgetArea, self.main)
        self.addDockWidget(Qt.RightDockWidgetArea, self.main_settings)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.settings)        

        """ Build tool bar"""
        # check button
        check_button = QAction(QIcon('icons/play.png'),
                'Check', self)
        check_button.setShortcut('Ctrl+R')
        check_button.setStatusTip('check setups')
        check_button.triggered.connect(self.check)

        # reset button
        reset_button = QAction(QIcon('icons/stop.png'),
                'Reset', self)
        reset_button.setShortcut('Ctrl+T')
        reset_button.setStatusTip('reset setups list')
        reset_button.triggered.connect(self.reset_lists)

        # update button
        update_button = QAction(QIcon('icons/reset.png'),
                'Update', self)
        update_button.setShortcut('Ctrl+Y')
        update_button.setStatusTip('update status')
        update_button.triggered.connect(self.update_status)


        toolbar = self.addToolBar('Control')
        toolbar.addAction(reset_button)
        toolbar.addAction(check_button)
        toolbar_1 = self.addToolBar('Control')
        toolbar_1.addAction(update_button)

        # status bar
        self.statusBar()
        
        # thread flow
        self.myThread = YourThreadName()
        #self.connect(self.get_thread, SIGNAL("finished()"), self.done)
        # executable methods for Main window's signals
    
    def check(self):
        print('check routine')        
        self.myThread.start()               
    
    def reset_lists(self):
        self.myThread.terminate()
        print('reset routine')
    
    def update_status(self):
        print('update status routine')
   
    def done(self):
        QMessageBox.information(self, "Done!", "Done fetching posts!")



class YourThreadName(QThread):

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def _get_post(self, inter):
        print('in _get_post')
        return inter+1

    def run(self):
        # your logic here
        print('run thread')
        count1=1
        while count1<10:            
            count1=self._get_post(count1)
            #self.emit(SIGNAL('add_post(QString)'), count1)            
            time.sleep(2)
            print('loop'+str(count1))


app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
