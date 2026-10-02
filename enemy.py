"""Lightweight patrol, investigation, and combat behavior for city NPCs."""

import math
import random


class Enemy:
    def __init__(self, x, y, police=False, tactical=False, aggressive=False):
        self.x, self.y = float(x), float(y)
        self.police = police
        self.tactical = tactical
        self.aggressive = aggressive or police or tactical
        self.angered = False
        self.health = 135 if tactical else (75 if police else 65)
        self.radius = 12
        self.state = "patrol"
        self.alert_time = 0.0
        self.cooldown = random.uniform(.2, 1.0)
        self.target = (x + random.randint(-140, 140), y + random.randint(-140, 140))
        self.color = (129, 149, 156) if tactical else ((82, 132, 151) if police else (150, 91, 77))

    def investigate(self, point):
        self.target = point
        self.alert_time = 8.0
        if self.aggressive:
            self.angered = True
            self.state = "alert"
        else:
            self.state = "investigate"

    def update(self, dt, player, bullets, collision_rects):
        self.cooldown = max(0, self.cooldown - dt)
        distance = math.hypot(player.x - self.x, player.y - self.y)
        if self.police and distance < 350:
            self.angered = True
        if self.angered and distance < 550:
            self.state = "alert"
            self.target = (player.x, player.y)
            self.alert_time = 5
        elif self.angered and self.alert_time > 0:
            self.alert_time -= dt
        elif self.angered:
            self.angered = False
            self.state = "patrol"
        elif self.alert_time > 0:
            self.alert_time -= dt
        else:
            self.state = "patrol"
            if math.hypot(self.target[0] - self.x, self.target[1] - self.y) < 18:
                self.target = (self.x + random.randint(-130, 130), self.y + random.randint(-130, 130))

        if distance > 185 or self.state != "alert":
            dx, dy = self.target[0] - self.x, self.target[1] - self.y
            length = math.hypot(dx, dy) or 1
            speed = 94 if self.state == "alert" else 44
            nx, ny = dx / length * speed * dt, dy / length * speed * dt
            candidate = (self.x + nx, self.y + ny)
            if not any(rect.collidepoint(candidate) for rect in collision_rects):
                self.x, self.y = candidate
        elif self.cooldown <= 0:
            bullets.append((self.x, self.y, player.x, player.y,
                            15 if self.tactical else (8 if self.police else 6)))
            self.cooldown = 1.1 if self.police else 1.45

    def damage(self, amount):
        self.health -= amount
        self.angered = True
        self.alert_time = 5.0
        self.state = "alert"
        return self.health <= 0