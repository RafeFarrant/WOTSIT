import qwiic_icm20948
import time
import sys

def main():
    # Initialize the IMU on the I2C bus
    IMU = qwiic_icm20948.QwiicIcm20948()

    if IMU.connected == False:
        print("SparkFun 9DoF IMU not detected. Check I2C wiring (SDA/SCL).", file=sys.stderr)
        return

    IMU.begin()
    print("IMU Connected. Calibrating, please keep robot completely still...")
    time.sleep(2)

    # Variables for tracking the robot's heading
    current_heading = 0.0
    last_time = time.time()
    
    # Gyroscope sensitivity scale factor (depends on sensor config, 131.0 is standard for +/- 250 dps)
    GYRO_SCALE = 131.0 

    while True:
        if IMU.dataReady():
            IMU.getAgmt() # Reads Accelerometer, Gyro, Magnetometer, and Temp
            
            current_time = time.time()
            dt = current_time - last_time # Time elapsed since last reading (Delta T)
            last_time = current_time

            # Get raw Z-axis rotation speed
            raw_gyro_z = IMU.gzRaw 
            
            # Convert raw data to Degrees Per Second (dps)
            rotation_speed_z = raw_gyro_z / GYRO_SCALE
            
            # Filter out tiny noise (deadband) when the robot is sitting perfectly still
            if abs(rotation_speed_z) < 1.0:
                rotation_speed_z = 0.0

            # Integrate the speed over time to get the total angle turned
            current_heading += (rotation_speed_z * dt)

            # Keep heading strictly between 0 and 360 degrees
            current_heading = current_heading % 360

            print(f"Turn Rate: {rotation_speed_z:5.1f} deg/s | Robot Heading: {current_heading:5.1f}°")
            
        time.sleep(0.02) # Run loop at roughly 50Hz

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped.")