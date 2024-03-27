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
        
        self.setWindowTitle('MODBUS RTU PROGRAMMING')        
        self.btnRead.clicked.connect(self.modbusRead)
        self.btnWrite.clicked.connect(self.modbusWrite)
        self.btnMultiWrite.clicked.connect(self.modbusMultiWrite)

        #radio buttons connection
        self.radioButtonString.setChecked(True)

    @pyqtSlot()
    def modbusRead(self):

        # Hata kontrolü ekleyelim
        try:
            readRegisterValue = instrument.read_register(int(self.registerNumber.text()),0) # Registernumber, number of decimals            
            self.value.setText(str(readRegisterValue))            
            self.liveWindow.append(str(readRegisterValue))
            self.faultMessage.setText("") 
        except ValueError:
            self.faultMessage.setText("Reading Address Not Enter!")     

        
        if gpio.input(led):
            gpio.output(led,gpio.LOW)
        else:
            gpio.output(led, gpio.HIGH)
            
    @pyqtSlot()
    def modbusWrite(self): 

        # Hata kontrolü ekleyelim
        try:
            instrument.write_register(int(self.registerNumber.text()), int(self.registerValue.text()), 0) # Registernumber, value, number of decimals for storage
            self.liveWindow.append("Writed")
            self.faultMessage.setText("") 
        except ValueError:
            self.faultMessage.setText("Writing Address or Value Not Enter!")           
        

        
        if gpio.input(led):
            gpio.output(led,gpio.LOW)
        else:
            gpio.output(led, gpio.HIGH)
    
    @pyqtSlot()
    def modbusMultiWrite(self):          

        print(self.registerMultiWriteStartNumber.text())
        print(self.multiWriteLine.text())

        # Hata kontrolü ekleyelim
        try:   
            self.faultMessage.setText("")

            #string selected
            if self.radioButtonString.isChecked():               
                
                ascii_array = [ord(char) for char in self.multiWriteLine.text()]
                print(ascii_array)
                print(type(ascii_array))

            else:

                text = self.multiWriteLine.text()  
                string_dizi = text.split(',')  
                integer_dizi = [int(x) for x in string_dizi]
                print(integer_dizi)
                print(type(integer_dizi))

                try:
                    instrument.write_registers(int(self.registerMultiWriteStartNumber.text()), integer_dizi)
                    self.liveWindow.append("Writed")
                    self.faultMessage.setText("") 
                except ValueError:
                    self.faultMessage.setText("MultiWrite Address Not Entered!") 

        except ValueError:
            self.faultMessage.setText("MultiWrite Address Not Entered or Invalid Number!")  
        
 
app=QApplication(sys.argv)
widget=HMI()
widget.show()
sys.exit(app.exec_())