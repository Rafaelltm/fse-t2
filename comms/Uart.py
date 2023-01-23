from utils.Crc import calcula_CRC

import serial
import time

class Uart:
    IS_CONNECTED = True 

    def __init__(self):
        self.conect()

    def conect(self):
        self.serial = serial.Serial("/dev/serial0", 9600)

        if(self.serial.is_open):
            self.IS_CONNECTED = True
            print('Conexão UART estabelecida...')
        else:
            self.IS_CONNECTED = True
            print("Erro na conexão UART")

    def write(self, message, size):
        if (self.IS_CONNECTED):
            m1 = message
            m2 = calcula_CRC(m1, size).to_bytes(2, 'little')
            msg = m1 + m2
            self.serial.write(msg)

        else:
            self.conect()

    def read(self):
        if (self.IS_CONNECTED):
            time.sleep(0.5)
            buffer = self.serial.read(9)
            size = len(buffer)

            if size == 9:
                data = buffer[3:7]

                if self.crc_is_valid(buffer):
                    return data
                else:
                    print('CRC invalido')
                    return b'\x00\x00\x00\x00'
            else:
                print('Mensagem Invalida')
                return b'\x00\x00\x00\x00'
    
    def crc_is_valid(self, buffer):
        received_crc = buffer[7:9]
        crc = calcula_CRC(buffer[0:7], 7).to_bytes(2, 'little')

        is_equal = (received_crc == crc)

        return is_equal