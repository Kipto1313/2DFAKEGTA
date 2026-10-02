"""Traffic and player-drivable vehicle model."""

import math
import pygame


VEHICLE_TYPES = {
    "Sedan": (195, (117, 130, 128)),
    "SUV": (175, (82, 100, 105)),
    "Sports Car": (245, (145, 76, 63)),
    "Muscle Car": (225, (147, 113, 62)),
    "Truck": (135, (103, 105, 91)),
    "Police Car": (210, (75, 103, 119)),
}


class Vehicle:
    def __init__(self, x, y, kind="Sedan", angle=0, traffic=False):
        self.x, self.y = float(x), float(y)
        self.kind = kind
        self.max_speed, self.color = VEHICLE_TYPES[kind]
        self.health = 100.0
        self.angle = angle
        self.speed = 0.0
        self.traffic = traffic
        self.occupied = False
        self.destroyed = False
        self.tire_damage = False

    def update(self, dt, keys=None, obstacles=()):
        if self.occupied and keys:
            accelerate = float(keys[pygame.K_w]) - float(keys[pygame.K_s])
            self.speed += accelerate * 265 * dt
            if not accelerate:
                self.speed *= max(0, 1 - 1.3 * dt)
            self.speed = max(-90, min(self.max_speed, self.speed))
            turn = float(keys[pygame.K_d]) - float(keys[pygame.K_a])
            self.angle += turn * (1.65 if abs(self.speed) > 20 else .7) * dt
            if self.tire_damage:
                self.angle += .2 * dt
        elif self.traffic:
            self.speed = 68
        old_x, old_y = self.x, self.y
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        bounds = self.rect
        if any(bounds.colliderect(obstacle) for obstacle in obstacles):
            self.x, self.y = old_x, old_y
            self.speed *= -.25

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 20), int(self.y - 12), 40, 24)

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.destroyed = True

    def draw(self, surface, camera):
        body = pygame.Surface((46, 30), pygame.SRCALPHA)
        pygame.draw.rect(body, self.color, (3, 4, 40, 22), border_radius=6)
        pygame.draw.rect(body, (42, 53, 55), (13, 6, 20, 18), border_radius=3)
        if self.kind == "Police Car":
            pygame.draw.rect(body, (179, 170, 133), (21, 3, 5, 3))
        rotated = pygame.transform.rotate(body, -math.degrees(self.angle))
        surface.blit(rotated, rotated.get_rect(center=(int(self.x - camera.x), int(self.y - camera.y))))