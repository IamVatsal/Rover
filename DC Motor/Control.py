import RPi.GPIO as GPIO
from time import sleep

class Motor:
    def __init__(self,Ena, In1, In2):
        self.Ena = Ena
        self.In1 = In1
        self.In2 = In2
        GPIO.setup(self.Ena, GPIO.OUT)
        GPIO.setup(self.In1, GPIO.OUT)
        GPIO.setup(self.In2, GPIO.OUT)
        self.pwm = GPIO.PWM(self.Ena, 100)
        self.pwm.start(0)

    def forward(self, speed,t=0): # Speed in percentage 0 to 100
        GPIO.output(self.In1, GPIO.HIGH)
        GPIO.output(self.In2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(speed)
        sleep(t)

    def backward(self, speed,t=0): # Speed in percentage 0 to 100
        GPIO.output(self.In1, GPIO.LOW)
        GPIO.output(self.In2, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(speed)
        sleep(t)
        self.stop()

    def stop(self,t=0):
        GPIO.output(self.In1, GPIO.LOW)
        GPIO.output(self.In2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)
        sleep(t)

motor1 = Motor(2,3,4)

while True:
    motor1.forward(50, 2)
    motor1.stop(2)
    motor1.backward(50, 2)
