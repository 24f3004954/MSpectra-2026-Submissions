import math
import random

class Drone:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0

        self.max_speed = 5
        self.max_force = 0.25

        self.angle = 0

        self.search_timer = 0
        self.search_direction = [0, 0]

        self.sensor_range = 80
        self.confidence = 0

        self.target_x = x
        self.target_y = y

        self.arrival_radius = 10
        self.slow_radius = 60
        self.arrived = False

    # ---------------- SEARCH ----------------
    def search(self):
        if self.search_timer <= 0:
            angle = random.uniform(0, 2 * math.pi)
            self.search_direction = [math.cos(angle), math.sin(angle)]
            self.search_timer = random.randint(30, 100)

        self.search_timer -= 1

        self.vx += self.search_direction[0] * 0.3
        self.vy += self.search_direction[1] * 0.3

    # ---------------- DETECTION ----------------
    def detect_target(self, target):
        dist = math.hypot(self.x - target[0], self.y - target[1])
        if dist < self.sensor_range:
            self.confidence += 1
            return True
        return False

    # ---------------- BOUNDARY ----------------
    def apply_boundary(self, width, height):
        margin = 50
        force = 0.5

        if self.x < margin:
            self.vx += force
        if self.x > width - margin:
            self.vx -= force
        if self.y < margin:
            self.vy += force
        if self.y > height - margin:
            self.vy -= force

    # ---------------- ARRIVAL ----------------
    def apply_arrival(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.arrival_radius:
            self.arrived = True
            self.vx *= 0.6
            self.vy *= 0.6

            if dist < 5:
                self.vx = 0
                self.vy = 0
            return

        self.arrived = False

        if dist > self.slow_radius:
            desired_speed = self.max_speed
        else:
            desired_speed = self.max_speed * (dist / self.slow_radius)

        if dist != 0:
            desired_vx = (dx / dist) * desired_speed
            desired_vy = (dy / dist) * desired_speed

            steer_x = desired_vx - self.vx
            steer_y = desired_vy - self.vy

            steer_mag = math.hypot(steer_x, steer_y)
            if steer_mag > self.max_force:
                steer_x = (steer_x / steer_mag) * self.max_force
                steer_y = (steer_y / steer_mag) * self.max_force

            self.vx += steer_x
            self.vy += steer_y

    # ---------------- COLLISION AVOIDANCE ----------------
    def apply_collision_avoidance(self, drones):
        separation_radius = 35
        repulsion_strength = 1.2

        steer_x = 0
        steer_y = 0
        count = 0

        for other in drones:
            if other.id == self.id:
                continue

            dx = self.x - other.x
            dy = self.y - other.y
            dist = math.hypot(dx, dy)

            if dist < separation_radius and dist > 0:
                nx = dx / dist
                ny = dy / dist

                force = (separation_radius - dist) / separation_radius

                steer_x += nx * force
                steer_y += ny * force
                count += 1

        if count > 0:
            steer_x /= count
            steer_y /= count

            mag = math.hypot(steer_x, steer_y)
            if mag > 0:
                steer_x = (steer_x / mag) * repulsion_strength
                steer_y = (steer_y / mag) * repulsion_strength

            self.vx += steer_x
            self.vy += steer_y

    # ---------------- EXECUTE INSTRUCTION ----------------
    def execute_instruction(self, instruction):
        cx, cy = instruction["target"]
        r = instruction["radius"]
        angle = instruction["angle"]

        self.target_x = cx + r * math.cos(angle)
        self.target_y = cy + r * math.sin(angle)

    # ---------------- UPDATE ----------------
    def update(self, mode="SEARCH", drones=None):

        if mode == "FORMATION":

            # 🔥 PRIORITY: avoid collision first
            if drones:
                self.apply_collision_avoidance(drones)

            # then move to target
            self.apply_arrival()

        speed = math.hypot(self.vx, self.vy)

        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed

        # 🔥 stronger damping → stability
        self.vx *= 0.90
        self.vy *= 0.90

        self.x += self.vx
        self.y += self.vy

        if speed > 0.2:
            target_angle = math.atan2(self.vy, self.vx)
            self.angle += (target_angle - self.angle) * 0.1