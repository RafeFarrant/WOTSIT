import sensor
import driving


def init():

    sensor_status = sensor.init()

    # Do not navigate if a sensor has failed.
    for name, working in sensor_status.items():

        if not working:
            raise RuntimeError(
                "Sensor initialisation failed: " + name
            )


def getWalls():

    sensor_status = sensor.status()

    for name, working in sensor_status.items():

        if not working:
            raise RuntimeError(
                "Sensor failure: " + name
            )

    return sensor.walls()


def wallFront():
    return getWalls()["front"]


def wallLeft():
    return getWalls()["left"]


def wallRight():
    return getWalls()["right"]


def moveForward():

    if wallFront():
        return

    driving.robot.forward_16(1)


def turnLeft():
    driving.robot.left(1)


def turnRight():
    driving.robot.right(1)


def stop():
    driving.robot.stop_both()


# These functions were originally used
# for displaying information in the simulator.
# They do not control physical hardware.

def setText(x, y, text):
    pass


def setColor(x, y, color):
    pass