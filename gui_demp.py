import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication,QDialog
from PyQt5.uic import loadUi
import RPi.GPIO as gpio
import minimalmodbus
import time 

led=17
 
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(led,gpio.OUT)

instrument = minimalmodbus.Instrument('/dev/ttyACM0', 1) # port name, slave address (in decimal)
 
class HMI(QDialog):   
    
    def __init__(self):
        super(HMI, self).__init__()
        loadUi('design.ui',self)
        
        self.setWindowTitle('Modbus RTU')        
        self.btnRead.clicked.connect(self.modbusRead)
        self.btnWrite.clicked.connect(self.modbusWrite)
        
    @pyqtSlot()
    def modbusRead(self):
        
        password = instrument.read_register(int(self.registerNumber.text()), 0) # Registernumber, number of decimals            
        self.value.setText(str(password))            
        self.liveWindow.append(str(password))
        
        if gpio.input(led):
            gpio.output(led,gpio.LOW)
        else:
            gpio.output(led, gpio.HIGH)
            
    @pyqtSlot()
    def modbusWrite(self):          
        
        instrument.write_register(int(self.registerNumber.text()), int(self.registerValue.text()), 0) # Registernumber, value, number of decimals for storage
        self.liveWindow.append("Writed")
        
        if gpio.input(led):
            gpio.output(led,gpio.LOW)
        else:
            gpio.output(led, gpio.HIGH)
        
 
app=QApplication(sys.argv)
widget=HMI()
widget.show()
sys.exit(app.exec_())