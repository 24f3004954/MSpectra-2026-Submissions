import math

def apply_collision_avoidance(drones, min_distance=20):
    for i in range(len(drones)):
        for j in range(i + 1, len(drones)):
            d1 = drones[i]
            d2 = drones[j]

            dx = d1.x - d2.x
            dy = d1.y - d2.y

            dist = math.hypot(dx, dy)

            if dist < min_distance and dist != 0:
                # Push them apart
                push = (min_distance - dist) / 2

                d1.x += push * (dx / dist)
                d1.y += push * (dy / dist)

                d2.x -= push * (dx / dist)
                d2.y -= push * (dy / dist)