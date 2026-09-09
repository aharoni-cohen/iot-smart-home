import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
#print(BASE_PATH)
import paho.mqtt.client as mqtt
#sys.path.insert(0,BASE_PATH.split('\\test')[0])
import time
import datetime

# Creating Client name - should be unique 
global clientname
r=random.randrange(1,10000) # for creating unique client ID
clientname="IOT_clientId-nXLMZeDcjH"+str(r)

class Mqtt_client():
    
    def __init__(self):
        # broker IP adress:
        self.broker=''
        self.topic='matzi/all'
        self.port='8000' # for using web sockets
        self.clientname=''
        self.username=''
        self.password=''        
        self.subscribeTopic=''
        self.publishTopic=''
        self.publishMessage=''
        self.on_connected_to_form = ''
        
    # Setters and getters
    def set_on_connected_to_form(self,on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form
    def get_broker(self):
        return self.broker
    def set_broker(self,value):
        self.broker= value         
    def get_port(self):
        return self.port
    def set_port(self,value):
        self.port= value     
    def get_clientName(self):
        return self.clientName
    def set_clientName(self,value):
        self.clientName= value        
    def get_username(self):
        return self.username
    def set_username(self,value):
        self.username= value     
    def get_password(self):
        return self.password
    def set_password(self,value):
        self.password= value         
    def get_subscribeTopic(self):
        return self.subscribeTopic
    def set_subscribeTopic(self,value):
        self.subscribeTopic= value        
    def get_publishTopic(self):
        return self.publishTopic
    def set_publishTopic(self,value):
        self.publishTopic= value         
    def get_publishMessage(self):
        return self.publishMessage
    def set_publishMessage(self,value):
        self.publishMessage= value 
        
        
    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)
            
    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("connected OK")
            self.on_connected_to_form();            
        else:
            print("Bad connection Returned code=",rc)
            
    def on_disconnect(self, client, userdata, flags, rc=0):
        print("DisConnected result code "+str(rc))
            
    def on_message(self, client, userdata, msg):
        topic=msg.topic
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        print("message from:"+topic, m_decode)
        #mainwin.subscribeDock.update_mess_win(m_decode)

    def connect_to(self):
        # Init paho mqtt client class        
        self.client = mqtt.Client(self.clientname, clean_session=True) # create new client instance        
        self.client.on_connect=self.on_connect  #bind call back function
        self.client.on_disconnect=self.on_disconnect
        self.client.on_log=self.on_log
        self.client.on_message=self.on_message
        self.client.username_pw_set(self.username,self.password)        
        print("Connecting to broker ",self.broker)
        # UnTNL
        #self.client.connect(self.broker,self.port)     #connect to broker
    
    def disconnect_from(self):
        self.client.disconnect() # disconnect
        print("disconnected")            
    
    def start_listening(self):        
        self.client.loop_start()
        #time.sleep(running_time)
    
    def stop_listening(self):        
        self.client.loop_stop()    
    
    def subscribe_to(self, topic):        
        #self.client.subscribe("matzi/0/3PI_16145805/sts")
        self.client.subscribe(topic)
              
    def publish_to(self, topic, message):
        self.client.publish(topic,message)        
        
    def relay_on(self,topic="matzi/0/", device_ID="3PI_16168238",on=True):            
        # Following is an example for code turning a Relay device 'On':
        if on:
            self.client.publish(topic+device_ID, ' {"type":"set_state", "action":"set_value", "addr":0, "cname":"ONOFF", "value":1}')
        else:
            # and consequently 'OFF':
            self.client.publish(topic+device_ID, ' {"type":"set_state", "action":"set_value", "addr":0, "cname":"ONOFF", "value":0}')
    
class MainDock(QDockWidget):
    """Main """
    def __init__(self,mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput=QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText("139.162.222.115")
        
        self.ePort=QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText("80")
        
        self.eClientID=QLineEdit()
        global clientname
        self.eClientID.setText(clientname)
        
        self.eUserName=QLineEdit()
        self.eUserName.setText("MATZI")
        
        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText("MATZI")
        
        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL=QCheckBox()
        
        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)
        
        self.eConnectbtn=QPushButton("Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: red")
        
        formLayot=QFormLayout()
        formLayot.addRow("Host",self.eHostInput )
        formLayot.addRow("Port",self.ePort )
        formLayot.addRow("Client ID", self.eClientID)
        formLayot.addRow("User Name",self.eUserName )
        formLayot.addRow("Password",self.ePassword )
        formLayot.addRow("Keep Alive",self.eKeepAlive )
        formLayot.addRow("SSL",self.eSSL )
        formLayot.addRow("Clean Session",self.eCleanSession )
        formLayot.addRow("",self.eConnectbtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        #self.setWindowTitle("Connect") 
        
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
            
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())
        print('on_button_connect_click')
        self.mc.connect_to()
        # open next one for starting loop
        self.mc.start_listening()
            
class PublishDock(QDockWidget):
    """Publisher """

    def __init__(self,mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        formLayot=QFormLayout()
                
        self.ePublisherTopic=QLineEdit()
        self.ePublisherTopic.setText("matzi/all")
        
        self.eQOS=QComboBox()
        self.eQOS.addItems(["0","1","2"])
        self.ePublishButton = QPushButton("Publish",self)
        self.eRetainCheckbox = QCheckBox();
        self.eMessageBox=QPlainTextEdit()        
        #eMessageBox.setTextCursor('{"type":"identify"}')        
        formLayot.addRow("Topic",self.ePublisherTopic)
        formLayot.addRow("QOS",self.eQOS)
        formLayot.addRow("Retain",self.eRetainCheckbox)
        formLayot.addRow("Message",self.eMessageBox)
        formLayot.addRow("",self.ePublishButton)
        
        self.ePublishButton.clicked.connect(self.on_button_publish_click)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setWidget(widget) 
        self.setWindowTitle("Publish") 
        
       
    def on_button_publish_click(self):
        self.mc.publish_to(self.ePublisherTopic.text(), self.eMessageBox.toPlainText())
        self.ePublishButton.setStyleSheet("background-color: yellow")
    
    
        
        
class SubscribeDock(QDockWidget):
    """Subscribe """

    def __init__(self,mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        
        self.eSubscribeTopic=QLineEdit()
        self.eSubscribeTopic.setText("matzi/#")
        self.eSubscribeButton = QPushButton("Subscribe",self)
        self.eSubscribeButton.clicked.connect(self.on_button_subscribe_click)
        
        self.eQOS = QComboBox()
        self.eQOS.addItems(["0","1","2"])
        
        self.eRecMess=QTextEdit()
        
        formLayot=QFormLayout()       
        formLayot.addRow("Topic",self.eSubscribeTopic)
        formLayot.addRow("QOS",self.eQOS)
        formLayot.addRow("Received",self.eRecMess)
        formLayot.addRow("",self.eSubscribeButton)
                
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setWidget(widget)
        self.setWindowTitle("Subscribe")
        
    def on_button_subscribe_click(self):
        print(self.eSubscribeTopic.text())
        self.mc.subscribe_to(self.eSubscribeTopic.text())
        self.eSubscribeButton.setStyleSheet("background-color: yellow")
    
    # create function that update text in received message window
    def update_mess_win(self,text):
        print('We are here')
		# UnTNL
        #self.eRecMess.append(text)
        
        
class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
                
        # Init of Mqtt_client class
        self.mc=Mqtt_client()
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 100, 600, 600)
        self.setWindowTitle('White Cubes GUI')        

        # Init QDockWidget objects        
        self.main =          MainDock(self.mc)        
        self.publishDock =   PublishDock(self.mc)
        self.subscribeDock = SubscribeDock(self.mc)
        
        self.addDockWidget(Qt.TopDockWidgetArea, self.main)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.publishDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.subscribeDock)
       

app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
