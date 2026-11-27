
import API

SIZE = 16

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

DX = [0, 1, 0, -1]
DY = [1, 0, -1, 0]

x = 0
y = 0

heading = NORTH

walls = [
    [
        [False, False, False, False]
        for _ in range(SIZE)
    ]
    for _ in range(SIZE)
]

distance = [
    [255 for _ in range(SIZE)]
    for _ in range(SIZE)
]


def set_boundary_walls():

    for x in range(SIZE):

        walls[x][0][SOUTH] = True
        walls[x][SIZE - 1][NORTH] = True

    for y in range(SIZE):

        walls[0][y][WEST] = True
        walls[SIZE - 1][y][EAST] = True


def add_wall(x, y, direction):

    walls[x][y][direction] = True

    nx = x + DX[direction]
    ny = y + DY[direction]

    if 0 <= nx < SIZE and 0 <= ny < SIZE:

        opposite = (direction + 2) % 4

        walls[nx][ny][opposite] = True


def can_move(x, y, direction):

    if walls[x][y][direction]:
        return False

    nx = x + DX[direction]
    ny = y + DY[direction]

    if nx < 0 or nx >= SIZE:
        return False

    if ny < 0 or ny >= SIZE:
        return False

    return True


def update_walls():

    detected = API.getWalls()

    if detected["front"]:
        add_wall(x, y, heading)

    if detected["left"]:
        add_wall(x, y, (heading + 3) % 4)

    if detected["right"]:
        add_wall(x, y, (heading + 1) % 4)


def flood_fill():

    for i in range(SIZE):

        for j in range(SIZE):

            distance[i][j] = 255

    targets = [
        (7, 7),
        (7, 8),
        (8, 7),
        (8, 8)
    ]

    queue = []

    for cell in targets:

        tx, ty = cell

        distance[tx][ty] = 0

        queue.append(cell)

    index = 0

    while index < len(queue):

        cx, cy = queue[index]

        index += 1

        for direction in range(4):

            if can_move(cx, cy, direction):

                nx = cx + DX[direction]
                ny = cy + DY[direction]

                new_distance = distance[cx][cy] + 1

                if new_distance < distance[nx][ny]:

                    distance[nx][ny] = new_distance

                    queue.append((nx, ny))


def choose_direction():

    best_direction = heading
    best_distance = 255

    for direction in range(4):

        if can_move(x, y, direction):

            nx = x + DX[direction]
            ny = y + DY[direction]

            if distance[nx][ny] < best_distance:

                best_distance = distance[nx][ny]

                best_direction = direction

    return best_direction


def turn_to(direction):

    global heading

    difference = (direction - heading) % 4

    if difference == 1:

        API.turnRight()

    elif difference == 2:

        API.turnRight()
        API.turnRight()

    elif difference == 3:

        API.turnLeft()

    heading = direction


def move_forward():

    global x, y

    API.moveForward()

    x += DX[heading]
    y += DY[heading]


def show_map():

    # Physical robot does not use simulator display.

    pass


def main():

    global x, y

    API.init()

    set_boundary_walls()

    try:

        while True:

            update_walls()

            flood_fill()

            show_map()

            if (x, y) in [
                (7, 7),
                (7, 8),
                (8, 7),
                (8, 8)
            ]:

                API.stop()

                print("Maze centre reached!")

                break

            direction = choose_direction()

            turn_to(direction)

            move_forward()

    finally:

        API.stop()


if __name__ == "__main__":

    main()
