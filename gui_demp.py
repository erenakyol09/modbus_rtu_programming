import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication,QDialog,QButtonGroup
from PyQt5.uic import loadUi
import minimalmodbus
from port_scanner import find_device_port

 
class HMI(QDialog):  
        
    def __init__(self):
        super(HMI, self).__init__()
        loadUi('design.ui',self)

        self.setWindowTitle('MODBUS RTU PROGRAMMING')       

        self.faultMessage.setText("")
        port = find_device_port(115200, 1)
        port_str = str(port)

        # İlk QButtonGroup oluştur
        self.radioButtonGroupMultiWrite = QButtonGroup()
        self.radioButtonGroupMultiWrite.addButton(self.radioButtonString)
        self.radioButtonGroupMultiWrite.addButton(self.radioButtonInteger)
        
        # İkinci QButtonGroup oluştur
        self.radioButtonGroupMultiRead = QButtonGroup()
        self.radioButtonGroupMultiRead.addButton(self.radioButtonMultiReadString)
        self.radioButtonGroupMultiRead.addButton(self.radioButtonMultiReadInteger)
        
        if port_str == "None":
            self.faultMessage.setText("Port Not Found!")
            self.btnRefresh.clicked.connect(self.scanner)
        else:
            self.connectionAllItem(port)


    @pyqtSlot()
    def connectionAllItem(self,port):
            
            port_str = str(port)
            self.instrument = minimalmodbus.Instrument(port, 1) # port name, slave address (in decimal)  
            self.faultMessage.setText(port_str)
            self.btnRead.clicked.connect(self.modbusRead)
            self.btnWrite.clicked.connect(self.modbusWrite)
            self.btnMultiWrite.clicked.connect(self.modbusMultiWrite)
            self.btnMultiRead.clicked.connect(self.modbusMultiRead)
            #radio buttons connection
            self.radioButtonString.setChecked(True)
            self.radioButtonMultiReadString.setChecked(True)

            
    
    @pyqtSlot()
    def scanner(self):

        self.faultMessage.setText("")
        port = find_device_port(115200, 1)
        port_str = str(port)

        
        if port_str == "None":
            self.faultMessage.setText("Port Not Found!")
        else:
            self.connectionAllItem(port)
                

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
        
    
    @pyqtSlot()
    def modbusMultiWrite(self):          

        # Hata kontrolü ekleyelim
        try:   
            self.faultMessage.setText("")

            #string selected
            if self.radioButtonString.isChecked():               
                
                ascii_array = [ord(char) for char in self.multiWriteLine.text()]

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

    @pyqtSlot()
    def modbusMultiRead(self):          
  
            self.faultMessage.setText("")
            self.multiReadArea.clear()

            try:
                    start_register = int(self.registerMultiReadStartNumber.text())
                    num_registers = int(self.registerMultiReadCount.text())

                    results = {}
                    for reg_num in range(start_register, start_register + num_registers):
                        try:
                            # Her bir register veya bobini oku ve sözlüğe ekle
                            result = self.instrument.read_register(reg_num, functioncode=3)  # Modbus RTU Read Holding Registers (03) komutu
                            results[reg_num] = result
                        except minimalmodbus.ModbusException as me:
                            self.faultMessage.setText(str(me)) 

                    #string selected
                    if self.radioButtonMultiReadString.isChecked():                           
                        # Map dictionary values to characters
                        characters = [chr(results[i]) for i in sorted(results.keys())]
                        # Concatenate characters to form a string
                        result_string = ''.join(characters)
                        self.multiReadArea.append(result_string)  
                    else:
                        # Extract values from the dictionary
                        values = results.values()
                        # Create a list from the values
                        result_list = list(values)
                        # Convert list elements to strings
                        result_strings = [str(item) for item in result_list]
                        # Join list elements with commas and spaces
                        result_str = ', '.join(result_strings)
                        self.multiReadArea.append(result_str)

            except Exception as e:
                    self.faultMessage.setText("MultiRead entry not integer!") 

            
                 
app=QApplication(sys.argv)
widget=HMI()
widget.show()
sys.exit(app.exec_())