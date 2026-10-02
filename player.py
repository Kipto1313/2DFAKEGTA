"""Player movement, stats, weapon selection, and vehicle state."""

import math
import pygame
from weapons import SPECS, Weapon


class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.radius = 12
        self.health, self.armor, self.stamina = 100.0, 35.0, 100.0
        self.cash, self.reputation = 280, 0
        self.inventory = ["Phone", "Evidence envelope"]
        self.unlocked = {"Pistol"}
        self.weapons = {spec.name: Weapon(spec) for spec in SPECS}
        self.weapon_index = 0
        self.angle = 0.0
        self.vehicle = None
        self.dodge_time = 0.0
        self.dodge_vector = (0.0, 0.0)
        self.flash = 0.0

    @property
    def weapon(self):
        return self.weapons[SPECS[self.weapon_index].name]

    def update(self, keys, dt, collision_rects):
        for weapon in self.weapons.values():
            weapon.update(dt)
        self.flash = max(0.0, self.flash - dt)
        if self.vehicle:
            self.x, self.y = self.vehicle.x, self.vehicle.y
            return
        dx = float(keys[pygame.K_d]) - float(keys[pygame.K_a])
        dy = float(keys[pygame.K_s]) - float(keys[pygame.K_w])
        length = math.hypot(dx, dy)
        speed = 235
        sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.stamina > 0 and length > 0
        if sprinting:
            speed = 345
            self.stamina = max(0, self.stamina - 29 * dt)
        else:
            self.stamina = min(100, self.stamina + 19 * dt)
        if self.dodge_time > 0:
            self.dodge_time = max(0, self.dodge_time - dt)
            dx, dy = self.dodge_vector
            speed = 610
        elif length:
            dx, dy = dx / length, dy / length
        self._move_axis(dx * speed * dt, 0, collision_rects)
        self._move_axis(0, dy * speed * dt, collision_rects)

    def _move_axis(self, dx, dy, obstacles):
        self.x += dx
        self.y += dy
        bounds = pygame.Rect(self.x - self.radius, self.y - self.radius,
                             self.radius * 2, self.radius * 2)
        for rect in obstacles:
            if bounds.colliderect(rect):
                if dx > 0:
                    self.x = rect.left - self.radius
                elif dx < 0:
                    self.x = rect.right + self.radius
                if dy > 0:
                    self.y = rect.top - self.radius
                elif dy < 0:
                    self.y = rect.bottom + self.radius
                bounds.center = (self.x, self.y)

    def dodge(self, keys):
        if self.vehicle or self.dodge_time > 0 or self.stamina < 22:
            return
        dx = float(keys[pygame.K_d]) - float(keys[pygame.K_a])
        dy = float(keys[pygame.K_s]) - float(keys[pygame.K_w])
        length = math.hypot(dx, dy) or 1
        self.dodge_vector = (dx / length, dy / length)
        self.dodge_time = .22
        self.stamina -= 22

    def take_damage(self, amount):
        absorbed = min(self.armor, amount * .55)
        self.armor -= absorbed
        self.health = max(0, self.health - (amount - absorbed))
        self.flash = .18

    def select_weapon(self, index):
        if 0 <= index < len(SPECS) and SPECS[index].name in self.unlocked:
            self.weapon_index = index

    def unlock_weapon(self, name):
        self.unlocked.add(name)