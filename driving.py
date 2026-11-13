# Import functions Pin, PWM and Sleep
from machine import Pin, PWM
from time import sleep

ticks_per_rev = 283
wheel_diameter = 40
mm_per_tick = (3.14159*wheel_diameter)/ticks_per_rev

# Define class motor
class motor:
    
    # Initialise the paremters and enable the minimum and maximum duty cycles
    def __init__(self, pinA, pinB, enable_pin, encoder_pin_a, encoder_pin_b, min_duty=0, max_duty=65535):
        self.pinA = pinA
        self.pinB= pinB
        self.enable_pin = enable_pin
        self.encoder_pin_a = encoder_pin_a
        self.encoder_pin_b = encoder_pin_b
        self.min_duty = min_duty
        self.max_duty = max_duty
        
        # Initialise encoder pin and set count to zero
        self.encoder_count = 0
        self.encoder_pin_a = encoder_pin_b
        self.encoder_pin_b = encoder_pin_b
        
        # Set up the encoder as an input with a pull-up resistor
        self.encoder_pin_a.init(Pin.IN, Pin.PULL_UP)
        self.encoder_pin_b.init(Pin.IN, Pin.PULL_UP)
        
        # Attach the interrupt 
        self.encoder_pin_a.irq(trigger=Pin.IRQ_RISING, handler=self.count_pulse)
        self.encoder_pin_b.irq(trigger=Pin.IRQ_RISING, handler=self.count_pulse)
    
    # Add one to encoder count on each pulse  
    def count_pulse(self, pin):
        self.encoder_count += 1

    # Reset encoder count to zero
    def reset_encoder(self) -> None:
        self.encoder_count = 0

    def duty_cycle(self, speed: float) -> int: 
        # Ensures that the speed is never more than 100% or less than 0%
        speed = max(0, min(100, speed))
        # Scale percentage to an integer 16-bit PWM duty cycle value 
        return int(self.min_duty + (self.max_duty - self.min_duty) * (speed / 100))
    
    
    # Define a function that turns the motor forwards
    def forward(self, speed: float) -> None:
        self.speed = speed
        self.enable_pin.duty_u16(self.duty_cycle(self.speed))
        self.pinA.value(1)
        self.pinB.value(0)
     
    # Define a function that turns the motor backwards     
    def backward(self, speed: float) -> None:
        self.speed = speed
        self.enable_pin.duty_u16(self.duty_cycle(self.speed))
        self.pinA.value(0)
        self.pinB.value(1)
        
        # Define a function that stops the motor
    def stop(self) -> None:
        self.speed = 0
        self.enable_pin.duty_u16(0)
        self.pinA.value(0)
        self.pinB.value(0)

# Initialise micromouse class
class micromouse:

    # Initialise the paremters and enable the minimum and maximum duty cycles
    def __init__(self, l_motor, r_motor):
        self.l_motor = l_motor
        self.r_motor = r_motor
        
    # Initialise a function to go straight forward      
    def straight(self, speed: float) -> None:
        
        # Turn the right & left motor forwards
        self.l_motor.forward(speed)
        self.r_motor.forward(speed)
    
    # Initialise a function to turn right 90 degrees      
    def left(self, speed: float) -> None:
        
        #STOP CORRECTING POSITION
        self.l_motor.reset_encoder()
        self.r_motor.reset_encoder()
        
        # Turn the right motor forwards and the left motor backwards
        self.l_motor.backward(speed)
        self.r_motor.forward(speed)
        
        while self.l_motor.encoder_count < ticks_per_rev and self.r_motor.encoder_count < ticks_per_rev:
            pass
            self.l_motor.stop()
            self.r_motor.stop()

                
    # Initialise a function to turn right 90 degrees      
    def right(self, speed: float) -> None:
        
        #STOP CORRECTING POSITION
        self.l_motor.reset_encoder()
        self.r_motor.reset_encoder()
        
        # Turn the left motor forwards and the right motor backwards
        self.l_motor.forward(speed)
        self.r_motor.backward(speed)
        
        while self.l_motor.encoder_count < ticks_per_rev and self.r_motor.encoder_count < ticks_per_rev:
            pass
            # Stop both both motors
            self.l_motor.stop()
            self.r_motor.stop()

    # Initialise a function to turn right 90 degrees      
    def forward_16(self, speed: float) -> None:
        
        #STOP CORRECTING POSITION
        self.l_motor.reset_encoder()
        self.r_motor.reset_encoder()
        
        target_ticks = 16 / mm_per_tick
        
        # Turn the right motor forwards and the left motor backwards
        self.straight(speed)
        
        while abs(self.l_motor.encoder_count) < target_ticks and abs(self.r_motor.encoder_count) < target_ticks:
            pass
            self.l_motor.stop()
            self.r_motor.stop()

    # Initialise a function for a left correction 
    def l_correction(self, speed: float) -> None:
        
        # Keep left motor at full speed and run the right motor at 90% speed
        self.l_motor.forward(1.0*speed)
        self.r_motor.forward(0.9*speed)
        
    # Initialise a function for a right correction    
    def r_correction(self, speed: float) -> None:
         
        # Keep right motor at full speed and run the left motor at 90% speed
        self.r_motor.forward(1.0*speed)
        self.l_motor.forward(0.9*speed)

    # Initialise a function to stop the mouse    
    def stop_both(self) -> None:
        self.l_motor.stop()
        self.r_motor.stop()
        

# Initialise frequency 
frequency = 1000

# Initialise pin outputs
pin1 = Pin(11, Pin.OUT)
pin2 = Pin(12, Pin.OUT)
pin3 = Pin(14, Pin.OUT)
pin4 = Pin(15, Pin.OUT)

# Encoder GPIO pins (make sure to update these to match your actual wiring!)
encoder_left_pin_a = Pin(26, Pin.IN)
encoder_left_pin_b = Pin(27, Pin.IN)
encoder_right_pin_a = Pin(20, Pin.IN)
encoder_right_pin_b = Pin(21, Pin.IN)


# Initialise PWMs
enable_m1 = PWM(Pin(10), freq=frequency)
enable_m2 = PWM(Pin(13), freq=frequency)

# Initialise right hand side motor
r_motor = motor(pin1, pin2, enable_m1, encoder_right_pin_a, encoder_right_pin_b)

# Initialise left hand side motor
l_motor = motor(pin3, pin4, enable_m2, encoder_left_pin_a, encoder_left_pin_b)

robot = micromouse(l_motor, r_motor)
    

