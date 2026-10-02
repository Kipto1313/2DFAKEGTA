"""Live Ashport simulation and gameplay orchestration."""

import math
import random
import pygame
from enemy import Enemy
from map import CityMap, WORLD_SIZE
from mission_manager import MissionManager
from player import Player
from vehicle import VEHICLE_TYPES, Vehicle


class Pedestrian:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.target = (x + random.randint(-90, 90), y + random.randint(-90, 90))
        self.phone = random.random() < .22
        self.panic = 0.0
        self.color = random.choice([(174, 147, 119), (127, 148, 143), (153, 119, 112)])

    def update(self, dt, gunshots):
        if any(math.hypot(self.x - x, self.y - y) < 380 for x, y in gunshots):
            self.panic = 4.0
        self.panic = max(0, self.panic - dt)
        dx, dy = self.target[0] - self.x, self.target[1] - self.y
        length = math.hypot(dx, dy)
        if length < 8:
            self.target = (self.x + random.randint(-110, 110), self.y + random.randint(-110, 110))
        elif self.panic:
            self.x -= dx / length * 105 * dt
            self.y -= dy / length * 105 * dt
        else:
            self.x += dx / length * 25 * dt
            self.y += dy / length * 25 * dt


class Camera:
    def __init__(self, width, height):
        self.x, self.y = 0.0, 0.0
        self.width, self.height = width, height
        self.zoom = 1.0
        self.shake = 0.0

    def update(self, player, dt):
        target_zoom = .82 if player.vehicle else 1.0
        self.zoom += (target_zoom - self.zoom) * min(1, dt * 4)
        view_w, view_h = self.width / self.zoom, self.height / self.zoom
        target_x = player.x - view_w / 2
        target_y = player.y - view_h / 2
        self.x += (target_x - self.x) * min(1, dt * 7)
        self.y += (target_y - self.y) * min(1, dt * 7)
        self.x = max(0, min(WORLD_SIZE[0] - view_w, self.x))
        self.y = max(0, min(WORLD_SIZE[1] - view_h, self.y))
        self.shake = max(0, self.shake - dt)

    def world_point(self, point):
        return self.x + point[0] / self.zoom, self.y + point[1] / self.zoom


class GameWorld:
    def __init__(self, width, height):
        self.map = CityMap()
        self.player = Player(950, 2680)
        self.missions = MissionManager()
        self.camera = Camera(width, height)
        self.enemies = [Enemy(1420, 2570), Enemy(1730, 2200), Enemy(2090, 1970)]
        self.pedestrians = [Pedestrian(random.randint(80, 4000), random.randint(80, 3400))
                            for _ in range(28)]
        self.vehicles = self._traffic()
        self.projectiles = []
        self.enemy_shots = []
        self.gunshots = []
        self.wanted = 0
        self.police_clock = 0
        self.crime_clock = 0
        self.weather_clock = 0
        self.weather = "CLEAR"
        self.day_time = 18.25
        self.message = "ASHPORT CITY  /  SOUTH DISTRICT"
        self.message_time = 5.0
        self.ending = ""
        self.game_over = False
        self.unlocked_districts = {"SOUTH DISTRICT", "DOWNTOWN", "MIDDLE CLASS", "OUTSKIRTS"}

    def _traffic(self):
        cars = []
        for index in range(12):
            y = 2650 + (index % 4) * 295
            x = 350 + (index * 347) % 3900
            cars.append(Vehicle(x, y + 30, random.choice(list(VEHICLE_TYPES)[:5]),
                                0 if index % 2 == 0 else math.pi, True))
        cars.append(Vehicle(900, 2685, "Sedan", 0, True))
        return cars

    def near_objective(self):
        return math.hypot(self.player.x - self.missions.target[0],
                          self.player.y - self.missions.target[1]) < 95

    def interact(self):
        if self.missions.complete:
            return
        if not self.near_objective():
            self.notify("Move closer to the objective.")
            return
        result = self.missions.interact(self.player, self.enemies)
        if result.get("mission_complete"):
            self.notify(result["reward"], 7)
            if self.missions.mission_index >= 2:
                self.unlocked_districts.add("INDUSTRIAL HARBOR")
        else:
            self.notify("CHECKPOINT UPDATED")

    def notify(self, text, duration=3.5):
        self.message, self.message_time = text, duration

    def fire(self, target):
        weapon = self.player.weapon
        if weapon.spec.melee:
            if weapon.cooldown or weapon.reload_left:
                return
            weapon.cooldown = weapon.spec.fire_delay
            candidates = []
            for enemy in self.enemies:
                dx, dy = enemy.x - self.player.x, enemy.y - self.player.y
                distance = math.hypot(dx, dy)
                angle = math.atan2(dy, dx)
                difference = math.atan2(math.sin(angle - self.player.angle),
                                        math.cos(angle - self.player.angle))
                if distance <= 62 and abs(difference) <= .9:
                    candidates.append((distance, enemy))
            if candidates:
                _, enemy = min(candidates, key=lambda candidate: candidate[0])
                if enemy.damage(weapon.spec.damage):
                    self.player.cash += 35
                self.wanted = min(5, max(1, self.wanted + 1))
                self.crime_clock = 14
            return
        origin = (self.player.x + math.cos(self.player.angle) * 17,
                  self.player.y + math.sin(self.player.angle) * 17)
        shots = weapon.fire(origin, target)
        if not shots:
            return
        self.projectiles.extend(shots)
        self.wanted = min(5, max(1, self.wanted + 1))
        self.gunshots.append((self.player.x, self.player.y))
        for enemy in self.enemies:
            if math.hypot(enemy.x - self.player.x, enemy.y - self.player.y) < 620:
                enemy.investigate((self.player.x, self.player.y))
        self.crime_clock = 14

    def toggle_vehicle(self):
        if self.player.vehicle:
            car = self.player.vehicle
            car.occupied = False
            self.player.vehicle = None
            self.player.x += math.cos(car.angle + math.pi / 2) * 36
            self.player.y += math.sin(car.angle + math.pi / 2) * 36
            self.notify("ON FOOT")
            return
        candidates = [car for car in self.vehicles if not car.destroyed and
                      math.hypot(car.x - self.player.x, car.y - self.player.y) < 58]
        if candidates:
            car = min(candidates, key=lambda item: math.hypot(item.x - self.player.x,
                                                               item.y - self.player.y))
            car.occupied = True
            car.traffic = False
            self.player.vehicle = car
            self.notify(f"STOLE {car.kind.upper()}  /  POLICE ALERT")
            self.wanted = max(1, self.wanted)
        else:
            self.notify("No vehicle close enough.")

    def update(self, dt, keys, mouse_position, firing):
        if self.game_over:
            return
        dt = min(dt, .05)
        self.day_time = (self.day_time + dt / 1200) % 24
        self.weather_clock += dt
        if self.weather_clock > 48:
            self.weather_clock = 0
            self.weather = random.choice(["CLEAR", "CLEAR", "RAIN", "FOG"])
        self.message_time = max(0, self.message_time - dt)
        self.missions.banner_time = max(0, self.missions.banner_time - dt)

        player = self.player
        player.update(keys, dt, self.map.collision_rects)
        world_mouse = self.camera.world_point(mouse_position)
        player.angle = math.atan2(world_mouse[1] - player.y, world_mouse[0] - player.x)
        if firing and player.vehicle is None:
            self.fire(world_mouse)

        for car in self.vehicles:
            car.update(dt, keys if car is player.vehicle else None, self.map.collision_rects)
            if not car.occupied and car.traffic:
                if car.x > WORLD_SIZE[0] + 30 or car.x < -30:
                    car.x = 0 if car.x < 0 else WORLD_SIZE[0]
        self.vehicles = [car for car in self.vehicles if not car.destroyed]

        for enemy in self.enemies:
            enemy.update(dt, player, self.enemy_shots, self.map.collision_rects)
        self._update_projectiles(dt)
        for pedestrian in self.pedestrians:
            pedestrian.update(dt, self.gunshots)
        if len(self.gunshots) > 12:
            self.gunshots = self.gunshots[-12:]

        self.crime_clock = max(0, self.crime_clock - dt)
        self.police_clock += dt
        if self.wanted and self.police_clock > max(2, 9 - self.wanted):
            self.police_clock = 0
            self.enemies.append(Enemy(player.x + random.randint(-330, 330),
                                      player.y + random.randint(-330, 330), police=True,
                                      tactical=self.wanted >= 4))
            if self.wanted >= 2:
                police_car = Vehicle(player.x + random.randint(-260, 260),
                                     player.y + random.randint(-260, 260),
                                     "Police Car", random.choice((0, math.pi / 2)), traffic=False)
                self.vehicles.append(police_car)
            if self.wanted >= 3:
                blocker = Vehicle(player.x + random.randint(-180, 180),
                                  player.y + random.randint(-180, 180),
                                  "Police Car", math.pi / 2, traffic=False)
                self.vehicles.append(blocker)
        if self.wanted and self.crime_clock <= 0 and not any(
                enemy.police and math.hypot(enemy.x - player.x, enemy.y - player.y) < 500
                for enemy in self.enemies):
            self.wanted = max(0, self.wanted - dt * .08)
        self.wanted = max(0, min(5, self.wanted))
        self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]
        self.camera.update(player, dt)

    def _update_projectiles(self, dt):
        remaining = []
        for bullet in self.projectiles:
            bullet.update(dt)
            if bullet.life <= 0 or not (0 <= bullet.x < WORLD_SIZE[0] and 0 <= bullet.y < WORLD_SIZE[1]):
                continue
            if any(rect.collidepoint(bullet.x, bullet.y) for rect in self.map.collision_rects):
                continue
            hit = False
            for enemy in self.enemies:
                if math.hypot(enemy.x - bullet.x, enemy.y - bullet.y) < enemy.radius + 3:
                    headshot = math.hypot(enemy.x - bullet.x, enemy.y - bullet.y) < 5
                    if enemy.damage(bullet.damage * (2 if headshot else 1)):
                        self.player.cash += 35
                    if headshot:
                        self.notify("HEADSHOT", 1.2)
                    hit = True
                    break
            if not hit:
                for car in self.vehicles:
                    if car.rect.collidepoint(bullet.x, bullet.y):
                        car.damage(bullet.damage * .45)
                        if car.destroyed:
                            self.camera.shake = .45
                            self.notify("VEHICLE DESTROYED", 2)
                        hit = True
                        break
            if not hit:
                remaining.append(bullet)
        self.projectiles = remaining

        incoming = []
        for x, y, tx, ty, damage in self.enemy_shots:
            dx, dy = tx - x, ty - y
            length = math.hypot(dx, dy) or 1
            dx, dy = dx / length * 260 * dt, dy / length * 260 * dt
            x, y = x + dx, y + dy
            if math.hypot(tx - x, ty - y) < 22:
                self.player.take_damage(damage)
                self.camera.shake = .16
            elif math.hypot(tx - x, ty - y) < 500:
                incoming.append((x, y, tx, ty, damage))
        self.enemy_shots = incoming
        if self.player.health <= 0:
            self.game_over = True

    def draw(self, screen, ui):
        shake_x = random.randint(-3, 3) if self.camera.shake else 0
        shake_y = random.randint(-3, 3) if self.camera.shake else 0
        view_w = max(1, round(screen.get_width() / self.camera.zoom))
        view_h = max(1, round(screen.get_height() / self.camera.zoom))
        scene = pygame.Surface((view_w, view_h))
        original_x, original_y = self.camera.x, self.camera.y
        self.camera.x -= shake_x / self.camera.zoom
        self.camera.y -= shake_y / self.camera.zoom
        self.map.draw(scene, self.camera)
        for car in self.vehicles:
            car.draw(scene, self.camera)
        for pedestrian in self.pedestrians:
            sx, sy = int(pedestrian.x - self.camera.x), int(pedestrian.y - self.camera.y)
            if -20 < sx < view_w + 20 and -20 < sy < view_h + 20:
                color = (186, 120, 100) if pedestrian.panic else pedestrian.color
                pygame.draw.circle(scene, color, (sx, sy), 6)
                if pedestrian.phone and not pedestrian.panic:
                    pygame.draw.line(scene, (190, 175, 139), (sx + 3, sy - 3), (sx + 5, sy - 7), 2)
        for enemy in self.enemies:
            sx, sy = int(enemy.x - self.camera.x), int(enemy.y - self.camera.y)
            if -30 < sx < view_w + 30 and -30 < sy < view_h + 30:
                pygame.draw.circle(scene, enemy.color, (sx, sy), enemy.radius)
                if enemy.state == "alert":
                    pygame.draw.circle(scene, (195, 91, 75), (sx, sy - 19), 3)
        if self.player.vehicle is None:
            px, py = int(self.player.x - self.camera.x), int(self.player.y - self.camera.y)
            tint = (231, 209, 171) if not self.player.flash else (245, 110, 93)
            pygame.draw.circle(scene, (18, 22, 23), (px + 2, py + 3), self.player.radius + 2)
            pygame.draw.circle(scene, tint, (px, py), self.player.radius)
            pygame.draw.line(scene, (39, 42, 40), (px, py),
                             (px + int(math.cos(self.player.angle) * 19),
                              py + int(math.sin(self.player.angle) * 19)), 4)
        for bullet in self.projectiles:
            pygame.draw.circle(scene, bullet.color,
                               (int(bullet.x - self.camera.x), int(bullet.y - self.camera.y)), 3)
        for x, y, _, _, _ in self.enemy_shots:
            pygame.draw.circle(scene, (229, 123, 90), (int(x - self.camera.x), int(y - self.camera.y)), 3)

        if self.day_time < 6 or self.day_time > 19:
            night = pygame.Surface(scene.get_size(), pygame.SRCALPHA)
            darkness = 74 if self.day_time < 5 or self.day_time > 21 else 40
            night.fill((12, 19, 28, darkness))
            scene.blit(night, (0, 0))
        if self.weather == "FOG":
            fog = pygame.Surface(scene.get_size(), pygame.SRCALPHA)
            fog.fill((159, 166, 157, 37))
            scene.blit(fog, (0, 0))
        if self.weather == "RAIN":
            for _ in range(70):
                x, y = random.randrange(view_w), random.randrange(view_h)
                pygame.draw.line(scene, (125, 151, 157), (x, y), (x - 4, y + 11), 1)
        self.camera.x, self.camera.y = original_x, original_y
        pygame.transform.smoothscale(scene, screen.get_size(), screen)
        ui.draw(screen, self)
