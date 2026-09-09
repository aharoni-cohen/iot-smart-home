import os
import sys
import PyQt5
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyaudio
import numpy as np
import smtplib
import time
import datetime

import paho.mqtt.client as mqtt
import random

class MainDock(QDockWidget):
    """Main """
    def __init__(self):
        QDockWidget.__init__(self)
        
        e1 = QLineEdit()
        e1.setValidator(QIntValidator())
        e1.setMaxLength(4)
        e1.setAlignment(Qt.AlignCenter)
        e1.setFont(QFont("Arial",20))
                 
        e2 = QLineEdit()
        e2.setValidator(QDoubleValidator(0.99,99.99,2))        
         
        e3 = QLineEdit()
        e3.setInputMask('99.999.999.999')        
         
        e4 = QLineEdit()
        e4.textChanged.connect(self.textchanged)        
         
        e5 = QLineEdit()
        e5.setEchoMode(QLineEdit.Password)
        e5.editingFinished.connect(self.enterPress)
         
        e6 = QLineEdit("Hello IOT developers")
        e6.setReadOnly(True)        
        
        flo = QFormLayout()
        flo.addRow("integer validator", e1)
        flo.addRow("Double validator",e2)
        flo.addRow("Input Mask",e3)
        flo.addRow("Text changed",e4)
        flo.addRow("Password",e5)
        flo.addRow("Read Only",e6)        
        
        widget = QWidget(self)
        widget.setLayout(flo)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)        
        
        
    def textchanged(self,text):
        print ("contents of text box: "+text)
    
    def enterPress(self):
        print ("edited, enter pressed")    

class SettingsDock(QDockWidget):
    """Settings """

    def __init__(self):
        QDockWidget.__init__(self)

        # size boxes
        size_y_box = QSpinBox(self)
        size_y_box.setMinimum(1)
        size_x_box = QSpinBox(self)
        size_x_box.setMinimum(2)

        # start/goal boxes
        start_y_box = QSpinBox(self)
        start_x_box = QSpinBox(self)
        goal_y_box = QSpinBox(self)
        goal_x_box = QSpinBox(self)

        # main box layout
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop|Qt.AlignLeft)

        temp_widget = QCheckBox("R")
        temp_widget.setCheckState(Qt.Checked)
        temp_widget.stateChanged.connect(lambda:self.btnstate(temp_widget))
        vbox.addWidget(temp_widget)
        vbox.addWidget(QCheckBox("T"))
        
        vbox.addWidget(QLabel("W"))
        hbox_world_size = QHBoxLayout()
        hbox_world_size.addWidget(QLabel("Y"))
        hbox_world_size.addWidget(size_y_box)
        hbox_world_size.addWidget(QLabel("X"))
        hbox_world_size.addWidget(size_x_box)
        world_size_widget = QWidget()
        world_size_widget.setLayout(hbox_world_size)
        vbox.addWidget(world_size_widget)

        vbox.addWidget(QLabel("S"))
        hbox_start = QHBoxLayout()
        hbox_start.addWidget(QLabel("Y"))
        hbox_start.addWidget(start_y_box)
        hbox_start.addWidget(QLabel("X"))
        hbox_start.addWidget(start_x_box)
        start_widget = QWidget()
        start_widget.setLayout(hbox_start)
        vbox.addWidget(start_widget)

        vbox.addWidget(QLabel("G"))
        hbox_goal = QHBoxLayout()
        hbox_goal.addWidget(QLabel("Y"))
        hbox_goal.addWidget(goal_y_box)
        hbox_goal.addWidget(QLabel("X"))
        hbox_goal.addWidget(goal_x_box)
        goal_widget = QWidget()
        goal_widget.setLayout(hbox_goal)
        vbox.addWidget(goal_widget)

        widget = QWidget(self)
        widget.setLayout(vbox)
        self.setWidget(widget)
        
        
    def btnstate(self,b):
        if b.isChecked() == True:
            print (b.text()+" is selected")
        else:
            print (b.text()+" is deselected")

class MainSettingsDock(QDockWidget):
    """Dock settings."""

    world_list = ["Plu", "Pla"]
    algo_list = ["Plu", "Pla"]
    heuristic_list = ["Plu", "Pla"]

    def __init__(self):
        QDockWidget.__init__(self)

        # 1 chooser
        self.world_combo = QComboBox()
        self.world_combo.addItems(MainSettingsDock.world_list)
        self.world_combo.setItemIcon(0, QIcon('icons/2d_4neigh.png'))
        self.world_combo.setItemIcon(1, QIcon('icons/2d_8neigh.png'))

        # 2 chooser
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(MainSettingsDock.algo_list)
        #self.connect(self.algo_combo, SIGNAL('currentIndexChanged(int)'),
        #        self.update_algo)

        # 3 chooser
        self.heuristic_combo = QComboBox()
        self.heuristic_combo.addItems(MainSettingsDock.heuristic_list)
        self.heuristic_combo.setItemIcon(0, QIcon('icons/heur_manhattan.png'))
        self.heuristic_combo.setItemIcon(1, QIcon('icons/heur_euclidean.png'))

        #  settings
        vbox = QVBoxLayout()
        #vbox.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
        vbox.addWidget(QLabel("Label1"))
        vbox.addWidget(self.world_combo)
        vbox.addWidget(QLabel("Label2"))
        vbox.addWidget(self.algo_combo)
        vbox.addWidget(QLabel("Label3"))
        vbox.addWidget(self.heuristic_combo)

        widget = QWidget()
        widget.setLayout(vbox)
        self.setWidget(widget)
  
class ConnectionDock(QDockWidget):
   
    def __init__(self):
        QDockWidget.__init__(self)
        
        ''' First Line '''        
        self.host = QVBoxLayout()
        self.host.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.host.addWidget(QLabel("Host"))        
        self.host.addWidget(QLineEdit('broker.mqttdashboard.com'))
        
        self.port = QVBoxLayout()
        self.port.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.port.addWidget(QLabel("Port"))        
        self.port.addWidget(QLineEdit('8000'))
        
        self.clientID = QVBoxLayout()
        self.clientID.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.clientID.addWidget(QLabel("Client ID"))        
        self.clientID.addWidget(QLineEdit('clientId-lyHPp5TXSy'))       
        
        self.connect = QVBoxLayout()
        self.connect.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.connect.addWidget(QLabel(" "))        
        self.connect.addWidget(QPushButton("Connect"))
        
        swidget1 = QWidget()
        swidget1.setLayout(self.host)
        
        swidget2 = QWidget()
        swidget2.setLayout(self.port)
        
        swidget3 = QWidget()
        swidget3.setLayout(self.clientID)
        
        swidget4 = QWidget()
        swidget4.setLayout(self.connect)
        
        self.fline = QHBoxLayout()
        self.fline.addWidget(swidget1)
        self.fline.addWidget(swidget2)
        self.fline.addWidget(swidget3)
        self.fline.addWidget(swidget4)
        ''' End of First Line '''      
        
       
        flo = QFormLayout()
        flo.addRow(self.fline)
        flo.addRow("Second Line: ",QLabel("Up to you!"))
     
        
        widget = QWidget(self)
        widget.setLayout(flo)
        widget.setFont(QFont("Arial",10))
        self.setTitleBarWidget(widget)
        self.setWidget(widget)        
        self.setWindowTitle('Connection')
        self.setFont(QFont("Arial",18))
      
      

class SubscriptionsDock(QDockWidget):
    

    def __init__(self):
        QDockWidget.__init__(self)


        
        self.setWindowTitle('Subscriptions')
        self.setFont(QFont("Arial",18)) 
           
    

class PublishDock(QDockWidget):
    

    def __init__(self):
        QDockWidget.__init__(self)
        
        
        
        self.setWindowTitle('Publish')
        self.setFont(QFont("Arial",18))
        
        
class MessagesDock(QDockWidget):
    

    def __init__(self):
        QDockWidget.__init__(self)
        
        
        
        
        self.setWindowTitle('Messages')
        self.setFont(QFont("Arial",18))
        
class soundMaker():
        
    def __init__(self,volume = 0.9,duration = 1.0,f = 800.0 ):
        p = pyaudio.PyAudio()
        
#         volume = 0.9     # range [0.0, 1.0]
        fs = 44100       # sampling rate, Hz, must be integer
#         duration = 1.0   # in seconds, may be float
#         f = 800.0        # sine frequency, Hz, may be float
        
        # generate samples, note conversion to float32 array
        #samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
        samples = (volume*np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32).tobytes()
        
        # for paFloat32 sample values must be in range [-1.0, 1.0]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=fs,
                        output=True)
        
        # play. May repeat with different volume values (if done interactively) 
        
        stream.write(samples)        
        stream.stop_stream()
        stream.close()        
        p.terminate()

class email():
    
    def __init__(self):
        pass        
    
    def send(self,from_addr, to_addr_list, cc_addr_list,
                  subject, message,
                  login, password,
                  smtpserver='smtp.gmail.com:587'):
        header  = 'From: %s' % from_addr
        header += 'To: %s' % ','.join(to_addr_list)
        header += 'Cc: %s' % ','.join(cc_addr_list)
        header += 'Subject: %s' % subject
        
        message = header + message
        try:
            server = smtplib.SMTP(smtpserver)
            server.starttls()
            server.login(login,password)
            problems = server.sendmail(from_addr, to_addr_list, message)
            server.quit()
        except:            
            print ("Error: unable to send email")    
        

class mqtt_client():
    
    def __init__(self,broker="139.162.222.115",port=80, clientname=''):
        # broker IP adress:
        self.broker=broker
        self.topic='matzi/all'
        self.port=port # for using web sockets
        self.clientname=clientname
        if clientname=='':            
            r=random.randrange(1,10000) # for creating unique client ID
            self.clientname="IOT_test-"+str(r)        
        
    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)
            
    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("connected OK")
        else:
            print("Bad connection Returned code=",rc)
            
    def on_disconnect(self, client, userdata, flags, rc=0):
        print("DisConnected result code "+str(rc))
            
    def on_message(self, client, userdata, msg):
        topic=msg.topic
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        print("message from:"+topic, m_decode)

    def connect_to(self, username="MATZI",password="MATZI"):        
        self.client = mqtt.Client(self.clientname, clean_session=True) # create new client instance        
        self.client.on_connect=self.on_connect  #bind call back function
        self.client.on_disconnect=self.on_disconnect
        self.client.on_log=self.on_log
        self.client.on_message=self.on_message
        self.client.username_pw_set(username,password)       
        print("Connecting to broker ",self.broker)
        self.client.connect(self.broker,self.port)     #connect to broker
    
    def disconnect_from(self):
        self.client.disconnect() # disconnect
        print("disconnected")            
    
    def start_listening(self):        
        self.client.loop_start()
        #time.sleep(running_time)
    
    def stop_listening(self):        
        self.client.loop_stop()    
    
    def subscribe_to(self, topic="matzi/#"):        
        #self.client.subscribe("matzi/0/3PI_16145805/sts")
        self.client.subscribe(topic)
              
    def publish_to(self, topic="matzi/all", message = '{"type":"identify"}'):
        self.client.publish(topic,message)        
        
    def relay_on(self,topic="matzi/0/", device_ID="3PI_16168238",on=True):            
        # Following is an example for code turning a Relay device 'On':
        if on:
            self.client.publish(topic+device_ID, ' {"type":"set_state", "action":"set_value", "addr":0, "cname":"ONOFF", "value":1}')
        else:
            # and consequently 'OFF':
            self.client.publish(topic+device_ID, ' {"type":"set_state", "action":"set_value", "addr":0, "cname":"ONOFF", "value":0}')
    

def main():
    # for debug purpose
    print('helpers debug')
    #soundMaker()
    
    # example of email class usage:
#     em=email()    
#     em.send(from_addr    = 'your@gmail.com', 
#           to_addr_list = ['your@gmail.com'],
#           cc_addr_list = ['your@gmail.com'], 
#           subject      = 'Howdy', 
#           message      = 'Howdy from a python function', 
#           login        = 'your@gmail.com', 
#           password     = 'your_password') 
    
    # example of mqtt_client class usage:    
    mc=mqtt_client()
    mc.connect_to()
    mc.start_listening()
    mc.subscribe_to()
    mc.publish_to()
    running_time = 60 # in sec
    time.sleep(running_time)
    mc.stop_listening()
    mc.disconnect_from()
    
    
    
    
    
    
    
      
            
if __name__ == '__main__':   
   main()     