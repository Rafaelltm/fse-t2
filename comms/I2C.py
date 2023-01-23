import smbus2
import bme280

class I2C:
    PORTA = 1
    ENDERECO = 0x76

    def __init__(self):
       pass

    def le_temperatura_da_sala(self):
        bus = smbus2.SMBus(self.PORTA)

        calibragem = bme280.load_calibration_params(bus, self.ENDERECO)
        sala = bme280.sample(bus, self.ENDERECO, calibragem)

        return sala.temperature