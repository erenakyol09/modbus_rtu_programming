import minimalmodbus
import serial.tools.list_ports

def find_device_port(baudrate, timeout):
    ports = serial.tools.list_ports.comports()

    for port in ports:
        port_name = port.device

        try:
            instrument = minimalmodbus.Instrument(port_name, 1)  # Bağlantı oluştur
            instrument.serial.baudrate = baudrate  # Bağlantı hızını ayarla
            instrument.serial.timeout = timeout  # Time-out süresini ayarla

            # Cihazdan veri okumaya çalış           
            try:
                model = instrument.read_register(0,0)          

            except minimalmodbus.ModbusException as me:
                #print("Cihaz bulundu!")
                return port_name


            # Eğer cihaz yanıt veriyorsa bu portu döndür
            if model:
                #print("Cihaz bulundu!")
                return port_name
        except Exception as e:
            pass  # Hata oluşursa devam et
    #print("Cihaz bulunamadı.")
    return None

def main():
    baudrate = 115200  # Seri port baud hızı
    timeout = 1  # Bağlantı time-out süresi (saniye cinsinden)

    port = find_device_port(baudrate, timeout)  # Cihazı bul
    print(port)

if __name__ == "__main__":
    main()
