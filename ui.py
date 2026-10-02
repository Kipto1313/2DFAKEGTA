"""Compact in-world HUD and Ashport minimap."""

import math
import pygame
from assets import ASSETS
from map import WORLD_SIZE


class GameUI:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.font = ASSETS.font(15)
        self.small = ASSETS.font(12)
        self.large = ASSETS.font(22, True)
        self.wasted = ASSETS.font(88, True)
        self.map_mask = pygame.Surface((184, 184), pygame.SRCALPHA)
        pygame.draw.circle(self.map_mask, (255, 255, 255, 255), (92, 92), 91)

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
        if weapon.spec.melee:
            status = "LMB TO PUNCH"
        else:
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
        if world.game_over:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((8, 9, 10, 180))
            screen.blit(overlay, (0, 0))
            title = self.wasted.render("WASTED", True, (190, 48, 43))
            screen.blit(title, title.get_rect(center=(width // 2, height // 2 - 10)))
            prompt = self.large.render("PRESS ENTER TO RESTART", True, (228, 220, 204))
            screen.blit(prompt, prompt.get_rect(center=(width // 2, height // 2 + 64)))

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
        size, center, scale = 184, 92, .08
        player_x, player_y = world.player.x, world.player.y
        visible = size / (2 * scale)
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.fill((91, 98, 91))

        def map_point(point):
            return (round(center + (point[0] - player_x) * scale),
                    round(center + (point[1] - player_y) * scale))

        water = pygame.Rect(4100, 1500, 500, 1700)
        water_rect = pygame.Rect(*map_point(water.topleft),
                                 round(water.width * scale), round(water.height * scale))
        pygame.draw.rect(surface, (43, 68, 73), water_rect)
        highway = pygame.Rect(0, 1450, 1600, 112)
        highway_rect = pygame.Rect(*map_point(highway.topleft),
                                   round(highway.width * scale), round(highway.height * scale))
        pygame.draw.rect(surface, (62, 67, 65), highway_rect)
        for track_y in (2240, 2255, 2270):
            pygame.draw.line(surface, (55, 61, 60), map_point((2700, track_y)),
                             map_point((4050, track_y)), 1)

        for rect, color, _ in world.map.buildings:
            if (rect.right < player_x - visible or rect.left > player_x + visible or
                    rect.bottom < player_y - visible or rect.top > player_y + visible):
                continue
            left, top = map_point(rect.topleft)
            block = pygame.Rect(left, top, max(2, round(rect.width * scale)),
                                max(2, round(rect.height * scale)))
            shade = tuple(max(48, min(125, channel + 22)) for channel in color)
            pygame.draw.rect(surface, shade, block)

        for road_x in range(0, WORLD_SIZE[0], 330):
            if abs(road_x - player_x) > visible + 80:
                continue
            x = round(center + (road_x - player_x) * scale)
            pygame.draw.rect(surface, (140, 145, 137),
                             (x, 0, max(3, round(78 * scale)), size))
            pygame.draw.line(surface, (164, 167, 157), (x + 1, 0), (x + 1, size), 1)
        for road_y in range(0, WORLD_SIZE[1], 295):
            if abs(road_y - player_y) > visible + 70:
                continue
            y = round(center + (road_y - player_y) * scale)
            pygame.draw.rect(surface, (140, 145, 137),
                             (0, y, size, max(3, round(68 * scale))))
            pygame.draw.line(surface, (164, 167, 157), (0, y + 1), (size, y + 1), 1)

        for _, point, _ in world.map.landmarks:
            if abs(point[0] - player_x) <= visible and abs(point[1] - player_y) <= visible:
                pygame.draw.circle(surface, (188, 157, 106), map_point(point), 3)

        mission_x, mission_y = world.missions.target
        marker_dx, marker_dy = (mission_x - player_x) * scale, (mission_y - player_y) * scale
        marker_length = max(1, math.hypot(marker_dx, marker_dy))
        if marker_length > 75:
            marker_dx, marker_dy = marker_dx / marker_length * 75, marker_dy / marker_length * 75
        marker = (round(center + marker_dx), round(center + marker_dy))
        pygame.draw.circle(surface, (25, 36, 30), marker, 9)
        mission_label = self.small.render("M", True, (139, 203, 127))
        surface.blit(mission_label, mission_label.get_rect(center=marker))

        direction = (math.cos(world.player.angle), math.sin(world.player.angle))
        side = (-direction[1], direction[0])
        player_marker = [
            (round(center + direction[0] * 10), round(center + direction[1] * 10)),
            (round(center - direction[0] * 6 + side[0] * 5),
             round(center - direction[1] * 6 + side[1] * 5)),
            (round(center - direction[0] * 6 - side[0] * 5),
             round(center - direction[1] * 6 - side[1] * 5)),
        ]
        pygame.draw.polygon(surface, (224, 222, 204), player_marker)
        surface.blit(self.map_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        pygame.draw.circle(screen, (23, 30, 29), (origin[0] + center, origin[1] + center), 95)
        screen.blit(surface, origin)
        pygame.draw.circle(screen, (91, 131, 102), (origin[0] + center, origin[1] + center), 92, 2)
        north = self.small.render("N", True, (219, 222, 206))
        screen.blit(north, north.get_rect(center=(origin[0] + center, origin[1] + 13)))
