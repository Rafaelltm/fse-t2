from comms.Uart import Uart
import utils.constants as Constants
from utils.Pid import PID
import struct
from comms.I2C import I2C
from Forno import Forno
import time
from threading import Thread
from utils.log import Logger
import datetime

class Main():
    uart = Uart()
    pid = PID()
    forno = Forno()
    i2c = I2C()
    logger = Logger()

    ref_temp = 0
    internal_temp = 0
    state = 0
    room_temp = 0

    def __init__(self):
        log_thread = Thread(target=self.registra_log, args=())
        log_thread.start()

        self.menu()

    def menu(self):
        while(True):
            time.sleep(2)
            if self.state == Constants.LIGAR_SISTEMA: #COMANDO 161
                self.sys_on()

            elif self.state == Constants.DESLIGAR_SISTEMA: #COMANDO 162
                self.sys_off()
                    
            elif self.state == Constants.LIGAR_FORNO: #COMANDO 163
                self.forno_on()

            elif self.state == Constants.DESLIGAR_FORNO: #COMANDO 164
                self.forno_off()

            else:
                pass 

    def atualiza_temperaturas(self):
        self.atualiza_ref_temp()
        self.atualiza_internal_temp()
        self.atualiza_room_temp()

    def atualiza_ref_temp(self):
        message = Constants.TEMPERATURA_REFERENCIA

        self.uart.write(message,  7)
        temperatura_response = self.uart.read()
        self.ref_temp = struct.unpack('f', temperatura_response)[0]
    
    def forno_off(self):
        message = Constants.SITUACAO_SISTEMA + b'\x00'
        self.uart.write(message,  8)
        data = self.uart.read()
        self.reseta_room_temp(data)
    
    def atualiza_internal_temp(self):
        message = Constants.TEMPERATURA_INTERNA

        self.uart.write(message,  7)
        temperatura_response = self.uart.read()
        self.internal_temp = struct.unpack('f', temperatura_response)[0]
    
    def atualiza_room_temp(self):
        self.room_temp = self.i2c.le_room_temp()
        
    def reseta_room_temp(self, data):
        if data == b'\x00\x00\x00\x00':
            print("Forno Desligado")
            if  self.internal_temp > self.room_temp:
                pid_de_referencia = self.pid.pid_controle(self.room_temp, self.internal_temp)
                if(pid_de_referencia < 0):
                        pid_de_referencia *= -1
                        if(pid_de_referencia < 40):
                            pid_de_referencia = 40
                self.forno.esfria(pid_de_referencia)

            elif self.internal_temp < self.room_temp:
                self.forno.esquenta(self.pid.pid_controle(self.room_temp, self.internal_temp))

    def sys_on(self):
        message = Constants.LIGAR_DESLIGAR_SISTEMA + b'\x01'
        self.uart.write(message,  8)
        data = self.uart.read()
        if data == b'\x01\x00\x00\x00':
            print("Sistema Ligado")
    
    def sys_off(self):
        message = Constants.LIGAR_DESLIGAR_SISTEMA + b'\x00'
        self.uart.write(message,  8)
        data = self.uart.read()

        if data == b'\x00\x00\x00\x00':
            print("Sistema Desligado")
    
    def forno_on(self):
        self.liga_led_funcionamento()

        while self.state != Constants.DESLIGAR_FORNO:
            self.trata_funcionamento_forno()
            
        self.forno_off()

    def liga_led_funcionamento(self):
        message = Constants.SITUACAO_SISTEMA + b'\x01'
        self.uart.write(message,  8)
        data = self.uart.read()
        
        if data == b'\x01\x00\x00\x00':
            print("Forno Ligado")

    def trata_funcionamento_forno(self):
        pid_de_referencia = self.pid.pid_controle(self.ref_temp, self.internal_temp)            
        if(pid_de_referencia < 0):
            pid_de_referencia *= -1
            if(pid_de_referencia < 40):
                pid_de_referencia = 40
            print("Resfriando...")
            self.forno.esfria(pid_de_referencia)
        else: 
            print("Esquentando...")   
            self.forno.esquenta(pid_de_referencia)

        time.sleep(1)

    def registra_log(self):
        cabecalho = ['TemperaturaInterna', 'TemperaturaReferencia', 'TemperaturaAmbiente', 'PID', "Data" ]
        self.logger.write(cabecalho)

        while True:
            data = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            self.le_comando_usuario()
            self.atualiza_temperaturas()
            line = [self.internal_temp, self.ref_temp, self.room_temp , self.pid.sinal_de_controle, data]
            self.logger.write(line)
            time.sleep(1)
    
    def le_comando_usuario(self):
        self.response = 0
        self.uart.write(Constants.COMANDO_DO_USUARIO,  7)

        state = self.uart.read()
        self.state = struct.unpack('i', state)[0]
        if self.state != 0:
            print("Comando: ", self.state)

if __name__ == '__main__':
    Main()