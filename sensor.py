from machine import Pin, I2C
import time
import math
from adafruit_vl53l0x import VL53L0X

I2C_ID = 0
SDA_PIN = 4
SCL_PIN = 5
I2C_FREQ = 400000

SENSORS = {
    "front": (2, 0x30,0), # each sensor is defined through their pin number
    "left":  (3, 0x31,0), # includes offset to be found at a later date 
    "right": (6, 0x32,0),
}

TIMING_BUDGET = 33000 # default mode 
RESET_DELAY_MS = 10 # time allowed for reset datasheet quotes 1.2ms
IO_TIMEOUT_S = 0.5 # time allowed for if no response leads to error

NOTHING_SEEN_MM = 8190 # error read from the tof sensors when nothing is in range
# work these all out 
FRONT_NO_WALL_MM = 150
SIDE_NO_WALL_MM = 75
ANGLE = 45
TARGET_SIDE_MM = 60


DIAG = math.cos(math.radians(ANGLE)) # find cos(45)
SENSOR_ERRORS = (OSError, RuntimeError) # a list of errors for the driver to report
#OSError is the I2C bus itself failing (a loose wire)
#RuntimeError the drivers checks failed

#three dictionaries each with different purposes
_tofs = {}  #three sensor objects created
_last = {"front": None, "left": None, "right" : None} #the last good reading from the sensor, starts as none as no reading
_ok = {"front" : False, "left": False, "right" : False} # whether each sensor is functioning, false because they havent started

def _front_mm(raw):
    # the raw front reading giving distance in mm or none if clear ahead
    if raw >= NOTHING_SEEN_MM:
        return None
    distance = raw - SENSORS["front"][2]  # in order to find actual distance based off offsets within sensors
    if distance > FRONT_NO_WALL_MM:
        return None
    return distance

def _side_mm(raw, name):
    # the raw diagonal reading giving distance in mm or none if above threshold 
    if raw >= NOTHING_SEEN_MM:
        return None
    perpendicular_distance = (raw - SENSORS[name][2]) * DIAG
    if perpendicular_distance > SIDE_NO_WALL_MM:
        return None
    return perpendicular_distance

def init():
    # start each sensors and assign its address
    i2c = I2C(I2C_ID, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=I2C_FREQ)#creates I2C bus
    
    #first switch all the sensors off
    xshut = {}  # empty dictionary for the xshut pins
    for name, (pin,addr, off) in SENSORS.items(): # loop through each of the sensors
        xshut[name] = Pin(pin, Pin.OUT, value=0) # turn that sensor off and disappears from I2C bus
    time.sleep_ms(RESET_DELAY_MS) # 10ms pause
    
    
    for name, (pin,addr, off) in SENSORS.items(): # wake up one each at a time moving it to the new address
        xshut[name].value(1) # switch one sensor on
        time.sleep_ms(RESET_DELAY_MS) # 10ms pause
        try: # attempt to do this if not do the except
            tof = VL53L0X(i2c, io_timeout_s=IO_TIMEOUT_S) #create the sensor object and boots at 0x29
            tof.set_address(addr) # move it to its own address
            tof.measurement_timing_budget = TIMING_BUDGET # set the time per reading/timing budget
            tof.start_continuous() #start continous mode so it is constantly reading
            _tofs[name] = tof #stores the result
            _ok[name] = True #records success
        except SENSOR_ERRORS:
            xshut[name].value(0) #if anything goes wrong switches off so other sensors can work
            _ok[name] = False # records failure
    return status()
    
def read(): #latest distance, if no new distances returns last value
    for name, tof in _tofs.items(): #loop through the functioning sensors
        if not _ok[name]: #skip the broken sensors
            continue
        try: # attempt this 
            if tof.data_ready: # is there a new reading available
                raw = tof.range #collect the reading 
                if name == "front":  #
                    _last[name] = _front_mm(raw)
                else: 
                    _last[name] = _side_mm(raw,name)
        except SENSOR_ERRORS: # if sensors fails
            _ok[name] = False
            _last[name] = None
    return dict(_last) # return results 

def walls(): # is there a wall yes or no
    distance = read() #latest distances
    return {name: distance[name] is not None for name in distance} #one way to build a dictionary

def centring_error(): # how far off the wall
    distance = read() # latest distances
    l, r = distance["left"], distance["right"] # unpack the two side readings
    if l is not None and r is not None: # both walls present
        return (l-r)/2
    if l is not None: # one wall present
        return l-TARGET_SIDE_MM
    if r is not None: # one wall present
        return TARGET_SIDE_MM - r
    return 0 #no side walls

def status(): #which sensors are working
    return dict(_ok)
                    
    
        


    







