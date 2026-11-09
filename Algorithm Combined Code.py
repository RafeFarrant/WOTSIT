import sensor
import driving

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

TARGETS = [(7, 7), (7, 8), (8, 7), (8, 8)]

walls = [
    [[False, False, False, False] for _ in range(SIZE)]
    for _ in range(SIZE)
]

distance = [
    [255 for _ in range(SIZE)]
    for _ in range(SIZE)
]


def set_boundary_walls():
    for x0 in range(SIZE):
        walls[x0][0][SOUTH] = True
        walls[x0][SIZE - 1][NORTH] = True

    for y0 in range(SIZE):
        walls[0][y0][WEST] = True
        walls[SIZE - 1][y0][EAST] = True


def add_wall(x0, y0, direction):
    walls[x0][y0][direction] = True

    nx = x0 + DX[direction]
    ny = y0 + DY[direction]

    if 0 <= nx < SIZE and 0 <= ny < SIZE:
        opposite = (direction + 2) % 4
        walls[nx][ny][opposite] = True


def can_move(x0, y0, direction):
    if walls[x0][y0][direction]:
        return False

    nx = x0 + DX[direction]
    ny = y0 + DY[direction]

    return 0 <= nx < SIZE and 0 <= ny < SIZE


def update_walls():
    if API.wallFront():
        add_wall(x, y, heading)

    if API.wallLeft():
        add_wall(x, y, (heading + 3) % 4)

    if API.wallRight():
        add_wall(x, y, (heading + 1) % 4)


def flood_fill():
    for i in range(SIZE):
        for j in range(SIZE):
            distance[i][j] = 255

    queue = []

    for tx, ty in TARGETS:
        distance[tx][ty] = 0
        queue.append((tx, ty))

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
    best_direction = None
    best_distance = 255

    # Prefer continuing in the current direction when
    # multiple neighbours have the same distance.
    directions = [
        heading,
        (heading + 1) % 4,
        (heading + 3) % 4,
        (heading + 2) % 4
    ]

    for direction in directions:
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

    if difference == 0:
        return True

    if difference == 1:
        success = API.right()
    elif difference == 2:
        success = API.right()

        if success is False:
            return False

        success = API.right()
    else:
        success = API.left()

    if success is False:
        return False

    heading = direction
    return True


def move_forward():
    global x, y

    if API.wallFront():
        add_wall(x, y, heading)
        return False

    success = API.forward()

    if success is False:
        return False

    nx = x + DX[heading]
    ny = y + DY[heading]

    if not (0 <= nx < SIZE and 0 <= ny < SIZE):
        return False

    x = nx
    y = ny

    return True


def show_map():
    # Optional: the physical robot may not support simulator
    # display functions, so print diagnostic information instead.
    print("Position:", x, y)
    print("Heading:", heading)
    print("Distance to centre:", distance[x][y])


def main():
    set_boundary_walls()

    while True:
        update_walls()
        flood_fill()
        show_map()

        if (x, y) in TARGETS:
            API.stop()
            print("Centre reached")
            return

        direction = choose_direction()

        if direction is None:
            API.stop()
            print("No reachable neighbouring cell")
            return

        if not turn_to(direction):
            API.stop()
            print("Turn failed")
            return

        if not move_forward():
            API.stop()
            print("Movement failed")
            return


if __name__ == "__main__":
    try:
        main()
    finally:
        API.stop()

