import math

def generate_circle_positions(center, radius, num_drones):
    cx, cy = center
    positions = []

    for i in range(num_drones):
        angle = 2 * math.pi * i / num_drones
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions.append((x, y))

    return positions