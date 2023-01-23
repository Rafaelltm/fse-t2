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

    temperatura_de_referencia = 0
    temperatura_interna = 0
    state = 0
    temperatura_da_sala = 0

    def __init__(self):
        loggerT = Thread(target=self.registra_log, args=())
        loggerT.start()

        self.menu()

    def menu(self):
        while(True):
            time.sleep(2)
            if self.state == Constants.LIGAR_FORNO:
                self.liga_forno()

            elif self.state == Constants.DESLIGAR_FORNO:
                self.desliga_forno()
                    
            elif self.state == Constants.LIGAR_SISTEMA:
                self.liga_sistema()

            elif self.state == Constants.DESLIGAR_SISTEMA:
                self.desliga_led_funcionamento()

            else:
                pass 


    def atualiza_temperaturas(self):
        self.atualiza_temperatura_de_referencia()
        self.atualiza_temperatura_interna()
        self.atualiza_temperatura_da_sala()

    
    def atualiza_temperatura_de_referencia(self):
        message = Constants.TEMPERATURA_REFERENCIA

        self.uart.write(message,  7)
        temperatura_response = self.uart.read()
        self.temperatura_de_referencia = struct.unpack('f', temperatura_response)[0]
    
    def desliga_led_funcionamento(self):
        message = Constants.SITUACAO_SISTEMA + b'\x00'
        self.uart.write(message,  8)
        data = self.uart.read()
        self.reseta_temperatura_sala(data)
    
    def atualiza_temperatura_interna(self):
        message = Constants.TEMPERATURA_INTERNA

        self.uart.write(message,  7)
        temperatura_response = self.uart.read()
        self.temperatura_interna = struct.unpack('f', temperatura_response)[0]
    
    def atualiza_temperatura_da_sala(self):
        self.temperatura_da_sala = self.i2c.le_temperatura_da_sala()
        
    
    def reseta_temperatura_sala(self, data):
        if data == b'\x00\x00\x00\x00':
            print("Forno Desligado")
            if  self.temperatura_interna > self.temperatura_da_sala:
                pid_de_referencia = self.pid.pid_controle(self.temperatura_da_sala, self.temperatura_interna)
                if(pid_de_referencia < 0):
                        pid_de_referencia *= -1
                        if(pid_de_referencia < 40):
                            pid_de_referencia = 40
                self.forno.esfria(pid_de_referencia)

            elif self.temperatura_interna < self.temperatura_da_sala:
                self.forno.esquenta(self.pid.pid_controle(self.temperatura_da_sala, self.temperatura_interna))

    def liga_forno(self):
        message = Constants.LIGAR_DESLIGAR_SISTEMA + b'\x01'
        self.uart.write(message,  8)
        data = self.uart.read()
        if data == b'\x01\x00\x00\x00':
            print("Forno Ligado")
    
    def desliga_forno(self):
        message = Constants.LIGAR_DESLIGAR_SISTEMA + b'\x00'
        self.uart.write(message,  8)
        data = self.uart.read()

        if data == b'\x00\x00\x00\x00':
            print("Sistema Desligado")
    
    def liga_sistema(self):
        self.liga_led_funcionamento()

        while self.state != Constants.DESLIGAR_SISTEMA:
            self.trata_funcionamento_forno()
            
        self.desliga_led_funcionamento()

    def liga_led_funcionamento(self):
        message = Constants.SITUACAO_SISTEMA + b'\x01'
        self.uart.write(message,  8)
        data = self.uart.read()
        
        if data == b'\x01\x00\x00\x00':
            print("Sistema Ligado")

    def trata_funcionamento_forno(self):
        pid_de_referencia = self.pid.pid_controle(self.temperatura_de_referencia, self.temperatura_interna)            
        if(pid_de_referencia < 0):
            pid_de_referencia *= -1
            if(pid_de_referencia < 40):
                pid_de_referencia = 40
            print("Reduzindo temperatura")
            self.forno.esfria(pid_de_referencia)
        else: 
            print("Aumentando temperatura")   
            self.forno.esquenta(pid_de_referencia)

        time.sleep(1)

    def registra_log(self):
        cabecalho = ['TemperaturaInterna', 'TemperaturaReferencia', 'TemperaturaAmbiente', 'PID', "Data" ]
        self.logger.write(cabecalho)

        while True:
            data = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            self.le_comando_usuario()
            self.atualiza_temperaturas()
            line = [self.temperatura_interna, self.temperatura_de_referencia, self.temperatura_da_sala , self.pid.sinal_de_controle, data]
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