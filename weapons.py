"""Weapon definitions, ammunition and projectile behavior."""

from dataclasses import dataclass
import math
import random


@dataclass(frozen=True)
class WeaponSpec:
    name: str
    damage: float
    fire_delay: float
    magazine: int
    reserve: int
    reload_time: float
    spread: float
    speed: float
    color: tuple
    melee: bool = False


SPECS = [
    WeaponSpec("Fists", 26, .42, 0, 0, 0, 0, 0, (231, 209, 171), True),
    WeaponSpec("Pistol", 27, .28, 12, 60, 1.0, .045, 760, (242, 202, 123)),
    WeaponSpec("Revolver", 48, .55, 6, 36, 1.4, .025, 820, (252, 183, 103)),
    WeaponSpec("SMG", 17, .095, 30, 120, 1.35, .12, 740, (244, 194, 110)),
    WeaponSpec("Shotgun", 13, .65, 6, 30, 1.4, .24, 650, (255, 218, 145)),
    WeaponSpec("Carbine", 25, .16, 30, 120, 1.55, .055, 900, (255, 220, 129)),
    WeaponSpec("Sniper", 75, .9, 5, 25, 1.8, .008, 1200, (255, 241, 185)),
]


class Weapon:
    def __init__(self, spec):
        self.spec = spec
        self.ammo = spec.magazine
        self.reserve = spec.reserve
        self.cooldown = 0.0
        self.reload_left = 0.0

    def update(self, dt):
        self.cooldown = max(0.0, self.cooldown - dt)
        if self.reload_left > 0:
            self.reload_left -= dt
            if self.reload_left <= 0:
                loaded = min(self.spec.magazine - self.ammo, self.reserve)
                self.ammo += loaded
                self.reserve -= loaded

    def reload(self):
        if self.reload_left <= 0 and self.ammo < self.spec.magazine and self.reserve:
            self.reload_left = self.spec.reload_time
            return True
        return False

    def fire(self, origin, target):
        if self.cooldown or self.reload_left or self.ammo <= 0:
            return []
        self.ammo -= 1
        self.cooldown = self.spec.fire_delay
        count = 6 if self.spec.name == "Shotgun" else 1
        base_angle = math.atan2(target[1] - origin[1], target[0] - origin[0])
        shots = []
        for _ in range(count):
            angle = base_angle + random.uniform(-self.spec.spread, self.spec.spread)
            shots.append(Bullet(origin[0], origin[1], math.cos(angle) * self.spec.speed,
                                math.sin(angle) * self.spec.speed, self.spec.damage, self.spec.color))
        return shots


class Bullet:
    def __init__(self, x, y, vx, vy, damage, color):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.damage = damage
        self.color = color
        self.life = 1.25

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt