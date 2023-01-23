import RPi.GPIO as GPIO

class Forno:
    def __init__(self):
        PORTA_RESISTOR = 23
        PORTA_VENTOINHA = 24
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PORTA_RESISTOR, GPIO.OUT)
        GPIO.setup(PORTA_VENTOINHA, GPIO.OUT)
        
        self.ventoinha = GPIO.PWM(PORTA_VENTOINHA, 1000)
        self.ventoinha.start(0)
        
        self.resistor = GPIO.PWM(PORTA_RESISTOR, 1000)
        self.resistor.start(0)
    
    def esquenta(self, pid):
        self.resistor.ChangeDutyCycle(pid)

    def esfria(self, pid):
        self.ventoinha.ChangeDutyCycle(pid) 