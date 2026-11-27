#MOTOR DRIVER
#Motor driver => Raspberry Pi
#PWMA => pin GP10
#AI1 => pin GP11      
#AI2 => pin GP12
#PWMB => pin GP13
#BI1 => pin GP14      
#BI2 => pin GP15
#VM => battery +
#VCC => 3.3V
#GND => GND & battery -
#STBY => 3.3V
#Motor driver => Encoder
#Encoder pins are flipped	
#AO1 => GND      
#AO2 => B
#BO1 => GND      
#BO2 => B

#ENCODER
#M1 => GND
#M2 (Encoder left A) => pin GP26
#VCC (Encoder left B) => pin GP27
#M2 (Encoder right A) => pin GP20
#VCC (Encoder right B) => pin GP21 
#A => 3.3V
#B =>A02 / B02
#GND =>A01 / B01

# Import functions Pin, PWM and Sleep
from machine import Pin, PWM
from time import sleep, ticks_ms, ticks_diff

# Initialise conditions  
FREQUENCY = 10000
TICKS_PER_REV = 283
WHEEL_DIAMETER_MM = 40
WHEEL_BASE_MM = 75
TURN_SCALE = 1.0 #Do testing on this
MM_PER_TICK = (3.14159*WHEEL_DIAMETER_MM)/TICKS_PER_REV
TURN_TICKS = ((3.14159*WHEEL_BASE_MM)/4)/MM_PER_TICK * TURN_SCALE

# Define class motor
class Motor:
    
    # Initialise the paremters and enable the minimum and maximum duty cycles
    def __init__(self, pinA, pinB, enable_pin, enc_a, enc_b, freq=FREQUENCY, min_duty=0, max_duty=65535):
        self.pinA = Pin(pinA, Pin.OUT)
        self.pinB= Pin(pinB, Pin.OUT)
        self.enable_pin = PWM(Pin(enable_pin), freq=freq)
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.speed=0
        
        # Initialise encoder pin and set count to zero
        self.enc_count = 0        
        # Set up the encoder as an input with a pull-up resistor
        self.enc_a = Pin(enc_a, Pin.IN, Pin.PULL_UP)
        self.enc_b = Pin(enc_b, Pin.IN, Pin.PULL_UP)

        # Attach interrupt 
        self.enc_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.count_pulse)
        
    # Add one to encoder count on each pulse  
    def count_pulse(self, pin):
        self.enc_count += 1

    # Reset encoder count to zero
    def reset_encoder(self):
        self.enc_count = 0

    def duty_cycle(self, speed) -> int: 
        # Ensures that the speed is never more than 100% or less than 0%
        speed = max(0, min(100, speed))
        # Scale percentage to an integer 16-bit PWM duty cycle value 
        return int(self.min_duty + (self.max_duty - self.min_duty) * (speed / 100))
    
    
    # Define a function that turns the motor forwards
    def forward(self, speed):
        self.speed = speed
        self.enable_pin.duty_u16(self.duty_cycle(self.speed))
        self.pinA.value(1)
        self.pinB.value(0)
     
    # Define a function that turns the motor backwards     
    def backward(self, speed):
        self.speed = speed
        self.enable_pin.duty_u16(self.duty_cycle(self.speed))
        self.pinA.value(0)
        self.pinB.value(1)
        
    # Define a function that stops the motor
    def stop(self):
        self.speed = 0
        self.enable_pin.duty_u16(0)
        self.pinA.value(0)
        self.pinB.value(0)

# Initialise micromouse class
class Micromouse:

    # Initialise the paremters and enable the minimum and maximum duty cycles
    def __init__(self, l_motor, r_motor):
        self.l_motor = l_motor
        self.r_motor = r_motor
        
    # Initialise a function to go straight forward      
    def straight(self, speed):
        # Turn the right & left motor forwards
        self.l_motor.forward(speed)
        self.r_motor.forward(speed)
        
    # Initialise a function to go reset both encoders      
    def reset_encs(self):
        self.l_motor.reset_encoder()
        self.r_motor.reset_encoder()
    
    # Initialise a function to stop both motors      
    def stop_both(self):
        self.l_motor.stop()
        self.r_motor.stop()
        
    def turn(self, speed, direction, target_ticks, timeout_ms=3000):
        
        self.reset_encs()
        
        if direction == 1: # Turns the mouse right
            self.l_motor.forward(speed)
            self.r_motor.backward(speed)
        else: # Turns the mouse left
            self.l_motor.backward(speed)
            self.r_motor.forward(speed)
            
        l_done = False
        r_done = False
        start = ticks_ms()
        
        while not (l_done and r_done):
            if not l_done and self.l_motor.enc_count >= target_ticks:
                self.l_motor.stop()
                l_done = True
            if not r_done and self.r_motor.enc_count >= target_ticks:
                self.r_motor.stop()
                r_done = True
            if ticks_diff(ticks_ms(), start) > timeout_ms:  
                break    
                
        self.stop_both()      
               
    # Initialise a function to turn left 90 degrees      
    def left(self, speed, target_ticks=TURN_TICKS):        
        self.turn(speed, 0, target_ticks)
            
    # Initialise a function to turn right 90 degrees      
    def right(self, speed, target_ticks=TURN_TICKS):
        self.turn(speed, 1, target_ticks)

    # Initialise a function to drive forward 160mm      
    def forward_16(self, speed, c=0.2, timeout_ms=5000):
        
        self.reset_encs()
        start = ticks_ms()    
        target_ticks = 160 / MM_PER_TICK
            
        while True:
            l = self.l_motor.enc_count
            r = self.r_motor.enc_count
        
            correction = c * (l - r)
            
            if (l + r) / 2 >= target_ticks:
                break
            if ticks_diff(ticks_ms(), start) > timeout_ms:
                break
            
            self.l_motor.forward(speed - correction)
            self.r_motor.forward(speed + correction)
            
        self.stop_both()

# Initialise motors written in format motor(IN1, IN2, PWM, ENC_A, ENC_B) 
l_motor = Motor(11, 12, 10, 26, 27)
r_motor = Motor(14, 15, 13, 20, 21)

robot = Micromouse(l_motor, r_motor)
