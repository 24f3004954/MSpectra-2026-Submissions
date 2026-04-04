def assign_targets(drones, positions):
    for i, drone in enumerate(drones):
        drone.target_x = positions[i][0]
        drone.target_y = positions[i][1]