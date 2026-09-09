import sys
import time
import PyQt5
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# the next imports for using gui_helpers classes
from gui_helpers import *

def process():   
    print('some process run')

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)        
        
        w = QWidget()
        l = QLabel(w)
        l.setText("Hello IoT!")        
        l.move(50,20)        
                
        self.b1 = QPushButton("Connect")
        self.b1.setGeometry(QRect(11, 11, 10, 10))
        self.b1.setCheckable(True)
        #       self.b1.toggle()
        self.b1.clicked.connect(lambda:self.whichbtn(self.b1))
        self.b1.clicked.connect(self.btnstate)
        self.b1.setStyleSheet("background-color: red")      
        
        self.b2 = QPushButton('image')
        self.b2.setIcon(QIcon(QPixmap("icons\\stop.png")))
        self.b2.clicked.connect(lambda:self.whichbtn(self.b2))
        self.b2.setStyleSheet("background-color:#ff0aa0;")
        
        self.b3 = QPushButton("Disabled")
        self.b3.setEnabled(False)
        self.b3.clicked.connect(lambda:self.whichbtn(self.b2))
        self.b3.setStyleSheet("background-color:default")
        
        self.b4 = QLineEdit("Default")
        #self.b4.setDefault(True)
        #self.b4.setCheckable(True)
        #self.b4.clicked.connect(lambda:self.whichbtn(self.b4))
        #self.b4.clicked.connect(self.btnstate)
        self.b4.setStyleSheet("background-color:rgb(255,255,0)")        
        
        layout = QVBoxLayout()
        layout.addWidget(self.b1)
        layout.addWidget(self.b2)      
        layout.addWidget(self.b3)
        layout.addWidget(self.b4)
        layout.addWidget(l) 
        layout.addWidget(w)      
        self.setLayout(layout)
        self.setGeometry(30, 50, 300, 100)
        self.setWindowTitle("Button colors demo")
    
    def btnstate(self):
        if self.b1.isChecked():
            print ("button 1 pressed")
            process()
            volume = 1          
            duration = 1.5
            f = 400.0
            #soundMaker(volume,duration,f)
            self.mc=mqtt_client()
            self.mc.connect_to()
            self.mc.start_listening()
            self.mc.subscribe_to()
            self.mc.publish_to()                    
        else:
            print ("button 1 released")
            #soundMaker()
            self.mc.stop_listening()
            self.mc.disconnect_from()
            self.mc=None
        
        if self.b4.isChecked():
            print ("button 4 pressed")
            self.mc.relay_on("matzi/0/","3PI_16168238",True)
        else:
            print ("button 1 released")
            
        if self.b2.isChecked():
            print ("button 4 pressed")
            textt=self.b4.getText()
            print(textt)
        else:
            print ("button 1 released")    
            
                 
    def whichbtn(self,b):
       print ("clicked button is "+b.text())

def main():
   app = QApplication(sys.argv)
   ex = Form()
   ex.show()
   sys.exit(app.exec_())
    
if __name__ == '__main__':
   main() 