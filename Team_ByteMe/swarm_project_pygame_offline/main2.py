import pygame
import random
import math
import time

from models.drone import Drone
from agent.swarm_agent import SwarmAgent

pygame.init()

WIDTH, HEIGHT = 1250, 780
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 16)

# -------- DRAW DRONE (FACING TARGET) --------
def draw_drone(surface, drone, color, target, is_leader=False):
    size = 14 if is_leader else 10

    # face toward target (center)
    dx = target[0] - drone.x
    dy = target[1] - drone.y
    angle = math.atan2(dy, dx)

    points = [
        (size, 0),
        (-size, size/2),
        (-size, -size/2)
    ]

    rotated = []
    for px, py in points:
        rx = px * math.cos(angle) - py * math.sin(angle)
        ry = px * math.sin(angle) + py * math.cos(angle)
        rotated.append((drone.x + rx, drone.y + ry))

    pygame.draw.polygon(surface, color, rotated)
    pygame.draw.polygon(surface, (20, 20, 20), rotated, 1)

# -------- SWARM --------
drones = [Drone(i, random.randint(100, 800), random.randint(100, 600)) for i in range(5)]
target = [random.randint(200, 700), random.randint(200, 500)]

agent = SwarmAgent()

# -------- STATES --------
state = "SEARCH"
leader_id = None
broadcast_start = None

formation_locked = False
stable_counter = 0

current_radius = 80

start_time = None
reconfig_time = None

# -------- METRICS --------
avg_dist = 0
spread = 0
arrived = 0

comm_cost_naive = 0
comm_cost_agent = 0

collision_count = 0

# -------- PACKET SIM --------
packet_loss_prob = 0.3
delay_range = (0.2, 1.0)

pending_instructions = {}
received_drones = set()

retry_interval = 1.0
last_retry_time = 0

# -------- COMM --------
messages = []
instructions = {}

def log(msg):
    messages.append(msg)
    if len(messages) > 6:
        messages.pop(0)

# -------- TEXT --------
y = 0
def draw_line(text, color=(220, 220, 220)):
    global y
    txt = font.render(text, True, color)
    screen.blit(txt, (860, y))
    y += 18

def section(title):
    global y
    y += 5
    draw_line(title, (180, 180, 255))
    draw_line("----------------", (80, 80, 120))

# -------- MAIN LOOP --------
running = True
while running:
    clock.tick(60)
    screen.fill((15, 15, 20))

    now = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------- SEARCH --------
    if state == "SEARCH":
        for drone in drones:
            drone.search()
            drone.apply_boundary(WIDTH, HEIGHT)
            drone.update("SEARCH")

            if drone.detect_target(target):
                leader = max(drones, key=lambda d: d.confidence)
                leader_id = leader.id

                log(f"[LEADER] D{leader_id} detected")

                state = "BROADCAST"
                broadcast_start = now
                start_time = now
                break

    # -------- BROADCAST --------
    elif state == "BROADCAST":

        for drone in drones:
            drone.search()
            drone.apply_boundary(WIDTH, HEIGHT)
            drone.update("SEARCH")

        pygame.draw.circle(screen, (255, 255, 0),
                           (int(target[0]), int(target[1])), 60, 1)

        # communication lines
        if leader_id is not None:
            leader = drones[leader_id]
            for d in drones:
                if d.id != leader_id:
                    pygame.draw.line(screen, (255, 255, 0),
                                     (int(leader.x), int(leader.y)),
                                     (int(d.x), int(d.y)), 1)

        if now - broadcast_start > 1.5:

            pending_instructions.clear()
            received_drones.clear()

            instructions = agent.generate_instructions(drones, target, current_radius)

            comm_cost_naive = len(drones) * 2
            comm_cost_agent = len(drones) + 2

            for drone in drones:
                if random.random() < packet_loss_prob:
                    log(f"[COMM] ❌ D{drone.id}")
                    continue

                delay = random.uniform(*delay_range)
                pending_instructions[drone.id] = (instructions[drone.id], now + delay)

                log(f"[COMM] 📡 D{drone.id}")

            state = "FORMATION"

    # -------- FORMATION --------
    elif state == "FORMATION":

        # deliver
        for drone_id in list(pending_instructions.keys()):
            inst, delivery_time = pending_instructions[drone_id]

            if now >= delivery_time:
                drones[drone_id].execute_instruction(inst)
                received_drones.add(drone_id)
                log(f"[COMM] ✅ D{drone_id}")
                del pending_instructions[drone_id]

        # retry (SAFE)
        if now - last_retry_time > retry_interval:
            for drone in drones:
                if drone.id not in received_drones and drone.id not in pending_instructions:
                    delay = random.uniform(*delay_range)
                    pending_instructions[drone.id] = (instructions[drone.id], now + delay)
                    log(f"[COMM] 🔁 D{drone.id}")
            last_retry_time = now

        # metrics
        avg_dist = sum(math.hypot(d.x - target[0], d.y - target[1]) for d in drones) / len(drones)

        spread = sum((math.hypot(d.x - target[0], d.y - target[1]) - avg_dist) ** 2 for d in drones) / len(drones)

        arrived = sum(1 for d in drones if d.arrived)

        decision = agent.decide({
            "avg_dist": avg_dist,
            "spread": spread,
            "arrived": arrived,
            "collisions": collision_count
        })

        current_radius += (decision["radius"] - current_radius) * 0.03

        for drone in drones:
            drone.apply_boundary(WIDTH, HEIGHT)
            drone.update("FORMATION", drones)

        # collision
        collision_count = 0
        for i in range(len(drones)):
            for j in range(i+1, len(drones)):
                if math.hypot(drones[i].x - drones[j].x,
                              drones[i].y - drones[j].y) < 10:
                    collision_count += 1

        # convergence
        all_arrived = True
        for drone in drones:
            if math.hypot(drone.x - drone.target_x,
                          drone.y - drone.target_y) > 15:
                all_arrived = False

        if all_arrived:
            stable_counter += 1
        else:
            stable_counter = 0

        if stable_counter > 40 and not formation_locked:
            formation_locked = True
            reconfig_time = round(now - start_time, 2)
            log(f"[SYSTEM] Done {reconfig_time}s")

    # -------- DRAW --------
    pygame.draw.circle(screen, (255, 80, 80),
                       (int(target[0]), int(target[1])), 8)

    pygame.draw.circle(screen, (80, 80, 80),
                       (int(target[0]), int(target[1])),
                       int(current_radius), 1)

    for drone in drones:
        color = (80, 200, 255)

        if drone.arrived:
            color = (100, 255, 100)

        is_leader = drone.id == leader_id
        if is_leader:
            color = (255, 255, 0)

        draw_drone(screen, drone, color, target, is_leader)

    # -------- GUI --------
    pygame.draw.rect(screen, (25, 25, 30), (850, 0, 400, HEIGHT))

    y = 20

    section("SYSTEM")
    draw_line(f"Mode: {state}")

    section("LEADER")
    draw_line(f"D{leader_id}" if leader_id is not None else "None", (255,255,0))

    section("AGENT")
    if state == "FORMATION":
        draw_line(f"R:{round(current_radius,1)} S:{round(spread,1)}")
        draw_line(f"D:{round(avg_dist,1)} A:{arrived}")
    else:
        draw_line("Inactive")

    section("METRICS")
    if comm_cost_naive > 0:
        eff = ((comm_cost_naive - comm_cost_agent)/comm_cost_naive)*100
        draw_line(f"Eff:{round(eff,1)}%", (100,255,100))

    draw_line(f"N:{comm_cost_naive} A:{comm_cost_agent}")
    draw_line(f"Coll:{collision_count}",
              (255,100,100) if collision_count>0 else (100,255,100))
    draw_line(f"T:{reconfig_time if reconfig_time else '-'}")

    section("COMM")
    for msg in messages:
        draw_line(msg, (180,180,180))

    pygame.display.flip()

pygame.quit()