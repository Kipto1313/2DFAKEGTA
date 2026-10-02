"""Compact in-world HUD and Ashport minimap."""

import pygame
from assets import ASSETS


class GameUI:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.font = ASSETS.font(15)
        self.small = ASSETS.font(12)
        self.large = ASSETS.font(22, True)

    def _text(self, surface, text, pos, color=(224, 222, 208), font=None):
        surface.blit((font or self.font).render(str(text), True, color), pos)

    def draw(self, screen, world):
        player, mission = world.player, world.missions
        width, height = self.screen_size
        panel = pygame.Surface((420, 158), pygame.SRCALPHA)
        panel.fill((12, 16, 17, 205))
        screen.blit(panel, (20, 20))
        district = world.map.district_at((player.x, player.y))
        self._text(screen, f"{mission.title}  /  {district}", (34, 28), (216, 183, 123), self.small)
        self._text(screen, mission.objective, (34, 47), (235, 231, 216), self.large)
        for index, line in enumerate(self._wrap(mission.story, self.small, 386)[:2]):
            self._text(screen, line, (34, 78 + index * 15), (159, 166, 156), self.small)
        self._meter(screen, (34, 119, 142, 7), player.health / 100, (177, 82, 72))
        self._meter(screen, (184, 119, 90, 7), player.armor / 100, (91, 130, 148))
        self._meter(screen, (282, 119, 82, 7), player.stamina / 100, (175, 151, 93))
        self._text(screen, "HEALTH", (34, 128), (174, 166, 151), self.small)
        self._text(screen, "ARMOR", (184, 128), (174, 166, 151), self.small)
        self._text(screen, "STAMINA", (282, 128), (174, 166, 151), self.small)

        self._draw_minimap(screen, world, (width - 204, 20))
        weapon = player.weapon
        status = "RELOADING" if weapon.reload_left else f"{weapon.ammo:02d} / {weapon.reserve:03d}"
        self._text(screen, f"{weapon.spec.name.upper()}   {status}", (width - 206, 244), (236, 224, 199))
        self._text(screen, f"${player.cash:,}    REP {player.reputation:+d}", (width - 206, 267), (210, 192, 145))
        wanted = int(world.wanted)
        self._text(screen, f"WANTED  {'|' * wanted}{'-' * (5 - wanted)}",
               (width - 206, 291), (221, 171, 101), self.font)
        self._text(screen, f"{world.weather}  /  {int(world.day_time):02d}:00",
               (width - 206, 314), (151, 165, 158), self.small)

        if world.message_time > 0:
            banner = self.large.render(world.message, True, (238, 224, 194))
            rect = banner.get_rect(center=(width // 2, height - 63))
            background = rect.inflate(28, 16)
            pygame.draw.rect(screen, (12, 16, 17, 225), background, border_radius=3)
            screen.blit(banner, rect)
        elif world.near_objective():
            prompt = self.font.render("[F]   INTERACT", True, (234, 215, 178))
            screen.blit(prompt, prompt.get_rect(center=(width // 2, height - 48)))
        if mission.complete and not mission.choice:
            self._text(screen, "J  JUSTICE        V  REVENGE", (width // 2 - 126, height // 2 + 56),
                       (237, 220, 185), self.font)

    def _meter(self, surface, rect, fraction, color):
        rect = pygame.Rect(rect)
        pygame.draw.rect(surface, (52, 56, 54), rect, border_radius=3)
        fill = rect.copy()
        fill.width = max(0, int(rect.width * max(0, min(1, fraction))))
        pygame.draw.rect(surface, color, fill, border_radius=3)

    def _wrap(self, text, font, max_width):
        lines, line = [], ""
        for word in text.split():
            candidate = f"{line} {word}".strip()
            if line and font.size(candidate)[0] > max_width:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        return lines

    def _draw_minimap(self, screen, world, origin):
        x, y = origin
        surface = pygame.Surface((184, 176))
        surface.fill((28, 37, 39))
        scale_x, scale_y = 184 / 4600, 176 / 3600
        for road_x in range(0, 4600, 330):
            pygame.draw.rect(surface, (68, 73, 70), (int(road_x * scale_x), 0, 3, 176))
        for road_y in range(0, 3600, 295):
            pygame.draw.rect(surface, (68, 73, 70), (0, int(road_y * scale_y), 184, 3))
        for _, point, _ in world.map.landmarks:
            pygame.draw.circle(surface, (150, 126, 90), (int(point[0] * scale_x), int(point[1] * scale_y)), 2)
        tx, ty = world.missions.target
        pygame.draw.circle(surface, (203, 169, 110), (int(tx * scale_x), int(ty * scale_y)), 4)
        pygame.draw.circle(surface, (218, 213, 192),
                           (int(world.player.x * scale_x), int(world.player.y * scale_y)), 4)
        pygame.draw.rect(surface, (149, 155, 145), surface.get_rect(), 1)
        screen.blit(surface, origin)
