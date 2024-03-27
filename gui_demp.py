import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication,QDialog
from PyQt5.uic import loadUi
import RPi.GPIO as gpio
import minimalmodbus
import time 
from port_scanner import find_device_port

led=17
 
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(led,gpio.OUT)

 
class HMI(QDialog):  
        
    def __init__(self):
        super(HMI, self).__init__()
        loadUi('design.ui',self)

        self.setWindowTitle('MODBUS RTU PROGRAMMING')       

        self.faultMessage.setText("")
        port = find_device_port(115200, 1)
        port_str = str(port)
        
        if port_str == "None":
            self.faultMessage.setText("Port Not Found!")
            self.btnRefresh.clicked.connect(self.scanner)
        else:
            self.instrument = minimalmodbus.Instrument(port, 1) # port name, slave address (in decimal)  
            self.faultMessage.setText(port_str)
            self.btnRead.clicked.connect(self.modbusRead)
            self.btnWrite.clicked.connect(self.modbusWrite)
            self.btnMultiWrite.clicked.connect(self.modbusMultiWrite)
            #radio buttons connection
            self.radioButtonString.setChecked(True)
            #self.btnRefresh.clicked.connect(self.scanner)
    
    @pyqtSlot()
    def scanner(self):

        self.faultMessage.setText("")
        port = find_device_port(115200, 1)
        port_str = str(port)

        
        if port_str == "None":
            self.faultMessage.setText("Port Not Found!")
        else:
            self.instrument = minimalmodbus.Instrument(port, 1) # port name, slave address (in decimal)
            self.faultMessage.setText(port_str)
            self.btnRead.clicked.connect(self.modbusRead)
            self.btnWrite.clicked.connect(self.modbusWrite)
            self.btnMultiWrite.clicked.connect(self.modbusMultiWrite)
            #radio buttons connection
            self.radioButtonString.setChecked(True)
                

    @pyqtSlot()
    def modbusRead(self):

        # Hata kontrolü ekleyelim
        try:
            try:
                readRegisterValue = self.instrument.read_register(int(self.registerNumber.text()),0) # Registernumber, number of decimals            
                self.value.setText(str(readRegisterValue))            
                self.liveWindow.append(str(readRegisterValue))
                self.faultMessage.setText("") 
            except minimalmodbus.ModbusException as me:
                self.faultMessage.setText(str(me))                     

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
            try:
                self.instrument.write_register(int(self.registerNumber.text()), int(self.registerValue.text()), 0) # Registernumber, value, number of decimals for storage
                self.liveWindow.append("Writed")
                self.faultMessage.setText("") 
            except minimalmodbus.ModbusException as me:
                self.faultMessage.setText(str(me)) 

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

                try:
                    self.instrument.write_registers(int(self.registerMultiWriteStartNumber.text()), ascii_array)
                    self.liveWindow.append("Writed")
                    self.faultMessage.setText("") 
                except minimalmodbus.ModbusException as me:
                    if self.registerMultiWriteStartNumber.text() == "":
                        self.faultMessage.setText("MultiWrite Address Not Entered!") 
                    else:
                        self.faultMessage.setText(str(me)) 

            else:

                text = self.multiWriteLine.text()  
                string_dizi = text.split(',')  
                integer_dizi = [int(x) for x in string_dizi]
                print(integer_dizi)
                print(type(integer_dizi))

                try:
                    self.instrument.write_registers(int(self.registerMultiWriteStartNumber.text()), integer_dizi)
                    self.liveWindow.append("Writed")
                    self.faultMessage.setText("") 
                except minimalmodbus.ModbusException as me:
                    if self.registerMultiWriteStartNumber.text() == "":
                        self.faultMessage.setText("MultiWrite Address Not Entered!") 
                    else:
                        self.faultMessage.setText(str(me)) 

        except ValueError:
            if self.registerMultiWriteStartNumber.text() == "":
                self.faultMessage.setText("MultiWrite Address Not Entered!") 
            else:
                self.faultMessage.setText("Invalid Number!") 
        
 
app=QApplication(sys.argv)
widget=HMI()
widget.show()
sys.exit(app.exec_())