class SwarmAgent:

    def __init__(self):
        self.radius = 80
        self.prev_error = 0

    def decide(self, state):

        avg_dist = state["avg_dist"]
        spread = state["spread"]
        arrived = state["arrived"]
        collisions = state["collisions"]

        # -------- ERROR TERMS --------
        target_dist = 80   # ideal distance from target
        error = avg_dist - target_dist

        # -------- ADAPTIVE CONTROL --------

        # 1. Collision avoidance (highest priority)
        if collisions > 0:
            self.radius += 2

        # 2. Too spread out → tighten
        elif spread > 150:
            self.radius -= 1.5

        # 3. Too far → shrink formation
        elif error > 20:
            self.radius -= 1

        # 4. Converging → stabilize
        elif arrived > 3:
            self.radius -= 0.5

        # 5. Stable → minimal adjustment
        else:
            self.radius += (error * 0.01)

        # -------- LIMITS --------
        self.radius = max(40, min(150, self.radius))

        return {
            "radius": self.radius
        }

    # -------- INSTRUCTION GENERATION --------
    def generate_instructions(self, drones, target, radius):

        instructions = {}
        n = len(drones)

        # sort drones by distance → better assignment
        drones_sorted = sorted(
            drones,
            key=lambda d: ((d.x - target[0])**2 + (d.y - target[1])**2)
        )

        for i, drone in enumerate(drones_sorted):
            angle = 2 * 3.14159 * i / n

            instructions[drone.id] = {
                "radius": radius,
                "angle": angle,
                "target": target
            }

        return instructions