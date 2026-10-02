"""Procedural Ashport City street grid and runtime-drawn placeholder city art."""

import random
import pygame


WORLD_SIZE = (4600, 3600)
DISTRICTS = [
    ("SOUTH DISTRICT", pygame.Rect(0, 1850, 2100, 1750), (108, 73, 66)),
    ("DOWNTOWN", pygame.Rect(1700, 0, 1700, 1900), (103, 112, 113)),
    ("INDUSTRIAL HARBOR", pygame.Rect(2700, 1650, 1900, 1550), (95, 109, 105)),
    ("MIDDLE CLASS", pygame.Rect(1400, 1750, 1600, 1600), (107, 116, 99)),
    ("OUTSKIRTS", pygame.Rect(0, 0, 1600, 1900), (81, 105, 86)),
]


class CityMap:
    def __init__(self):
        random.seed(19)
        self.buildings = []
        self.collision_rects = []
        self.landmarks = []
        self._generate()

    def _generate(self):
        blocks_x = [(x + 88, min(x + 310, WORLD_SIZE[0]))
                for x in range(0, WORLD_SIZE[0], 330)]
        blocks_y = [(y + 76, min(y + 278, WORLD_SIZE[1]))
                for y in range(0, WORLD_SIZE[1], 295)]
        for left, right in blocks_x:
            for top, bottom in blocks_y:
                if right - left < 180 or bottom - top < 160:
                    continue
                for _ in range(random.randint(2, 5)):
                    width, height = random.randint(48, 112), random.randint(50, 128)
                    x = random.randint(left + 22, max(left + 22, right - width - 18))
                    y = random.randint(top + 20, max(top + 20, bottom - height - 16))
                    color = random.choice([(73, 77, 76), (89, 83, 77), (102, 91, 80),
                                           (67, 76, 78), (111, 105, 92)])
                    rect = pygame.Rect(x, y, width, height)
                    self.buildings.append((rect, color, random.choice([0, 1, 2])))
                    self.collision_rects.append(rect)
        self.landmarks = [
            ("THE FUNERAL", (980, 2830), "Cemetery"),
            ("MARCUS' APARTMENT", (695, 2440), "Safehouse"),
            ("REED'S LEAD", (1820, 2110), "Newsstand"),
            ("HARBOR GATE", (3580, 2460), "Harbor"),
            ("ASHPORT CIVIC", (2350, 640), "Government"),
            ("HALE TOWER", (2860, 470), "Skyscraper"),
        ]

    def district_at(self, point):
        for name, area, _ in DISTRICTS:
            if area.collidepoint(point):
                return name
        return "ASHPORT CITY"

    def draw(self, surface, camera):
        surface.fill((47, 55, 54))
        water = pygame.Rect(4100 - camera.x, 1500 - camera.y, 500, 1700)
        pygame.draw.rect(surface, (31, 49, 54), water)
        # A divided expressway and freight tracks distinguish the outer and port edges.
        highway = pygame.Rect(-camera.x, 1450 - camera.y, 1600, 112)
        pygame.draw.rect(surface, (38, 43, 44), highway)
        pygame.draw.line(surface, (133, 125, 99), (highway.x, highway.y + 55),
                         (highway.right, highway.y + 55), 3)
        for track_y in (2240, 2255, 2270):
            pygame.draw.line(surface, (37, 43, 43), (2700 - camera.x, track_y - camera.y),
                             (4050 - camera.x, track_y - camera.y), 3)
        for x in range(0, WORLD_SIZE[0], 330):
            sx = x - camera.x
            if sx < -330 or sx > surface.get_width() + 330:
                continue
            pygame.draw.rect(surface, (47, 52, 52), (sx, -camera.y, 78, WORLD_SIZE[1]))
            pygame.draw.line(surface, (94, 91, 80), (sx + 80, -camera.y),
                             (sx + 80, WORLD_SIZE[1] - camera.y), 5)
            for dash_y in range(0, WORLD_SIZE[1], 68):
                pygame.draw.line(surface, (142, 130, 103), (sx + 38, dash_y - camera.y),
                                 (sx + 38, dash_y + 30 - camera.y), 2)
        for y in range(0, WORLD_SIZE[1], 295):
            sy = y - camera.y
            if sy < -295 or sy > surface.get_height() + 295:
                continue
            pygame.draw.rect(surface, (46, 52, 52), (-camera.x, sy, WORLD_SIZE[0], 68))
            pygame.draw.line(surface, (94, 91, 80), (-camera.x, sy + 70),
                             (WORLD_SIZE[0] - camera.x, sy + 70), 5)
            for dash_x in range(0, WORLD_SIZE[0], 68):
                pygame.draw.line(surface, (140, 128, 101), (dash_x - camera.x, sy + 33),
                                 (dash_x + 30 - camera.x, sy + 33), 2)

        view = pygame.Rect(camera.x - 130, camera.y - 130,
                           surface.get_width() + 260, surface.get_height() + 260)
        for rect, color, kind in self.buildings:
            if not rect.colliderect(view):
                continue
            screen_rect = rect.move(-camera.x, -camera.y)
            pygame.draw.rect(surface, (29, 33, 33), screen_rect.move(5, 7), border_radius=2)
            pygame.draw.rect(surface, color, screen_rect, border_radius=2)
            roof_color = tuple(min(255, c + 15) for c in color)
            pygame.draw.rect(surface, roof_color, (screen_rect.x + 5, screen_rect.y + 5,
                                                   screen_rect.w - 10, 7))
            if kind:
                for wx in range(screen_rect.x + 10, screen_rect.right - 8, 18):
                    for wy in range(screen_rect.y + 20, screen_rect.bottom - 8, 24):
                        pygame.draw.rect(surface, (155, 139, 105), (wx, wy, 4, 6))
        for index in range(7):
            x, y = 3420 + (index % 3) * 165, 2040 + (index // 3) * 92
            rect = pygame.Rect(x - camera.x, y - camera.y, 142, 62)
            pygame.draw.rect(surface, [(109, 68, 54), (65, 83, 83), (124, 104, 68)][index % 3], rect)
            pygame.draw.line(surface, (25, 35, 35), rect.topleft, rect.bottomleft, 3)
        ship = pygame.Rect(4215 - camera.x, 2110 - camera.y, 285, 90)
        pygame.draw.rect(surface, (76, 76, 71), ship, border_radius=24)
        pygame.draw.rect(surface, (148, 134, 112), (ship.x + 46, ship.y + 20, 46, 26))
        self._draw_places(surface, camera)
        for label, pos, _ in self.landmarks:
            sx, sy = pos[0] - camera.x, pos[1] - camera.y
            if -120 < sx < surface.get_width() + 120 and -50 < sy < surface.get_height() + 50:
                pygame.draw.circle(surface, (201, 165, 105), (int(sx), int(sy)), 8, 2)

    def _draw_places(self, surface, camera):
        def rect_at(x, y, width, height):
            return pygame.Rect(x - camera.x, y - camera.y, width, height)

        court = rect_at(520, 2565, 135, 82)
        pygame.draw.rect(surface, (67, 74, 66), court)
        pygame.draw.rect(surface, (157, 119, 83), court.inflate(-12, -12), 2)
        pygame.draw.line(surface, (157, 119, 83), (court.centerx, court.top + 6),
                 (court.centerx, court.bottom - 6), 2)
        for hoop_x in (court.left + 12, court.right - 12):
            pygame.draw.circle(surface, (194, 151, 94), (hoop_x, court.centery), 5, 2)

        cemetery = rect_at(900, 2760, 210, 155)
        pygame.draw.rect(surface, (67, 75, 66), cemetery)
        pygame.draw.rect(surface, (113, 118, 101), cemetery, 2)
        for grave_y in range(cemetery.y + 18, cemetery.bottom - 12, 27):
            for grave_x in range(cemetery.x + 18, cemetery.right - 14, 29):
                pygame.draw.rect(surface, (140, 140, 120), (grave_x, grave_y, 8, 4))

        park = rect_at(1470, 2320, 175, 125)
        pygame.draw.rect(surface, (57, 77, 61), park)
        pygame.draw.line(surface, (114, 119, 96), park.topleft, park.bottomright, 5)
        for tree_x, tree_y in ((25, 24), (70, 25), (135, 24), (45, 93), (118, 88)):
            pygame.draw.circle(surface, (37, 57, 45), (park.x + tree_x, park.y + tree_y), 12)
            pygame.draw.circle(surface, (94, 109, 76), (park.x + tree_x, park.y + tree_y), 7)

        school = rect_at(1720, 1780, 150, 88)
        pygame.draw.rect(surface, (121, 108, 88), school)
        pygame.draw.rect(surface, (168, 148, 108), (school.centerx - 16, school.y + 10, 32, 23))
        pygame.draw.rect(surface, (73, 84, 76), rect_at(1885, 1782, 95, 64))

        for tree_x in range(100, 1320, 82):
            for tree_y in range(180, 1320, 94):
                if (tree_x + tree_y) % 4:
                    center = (int(tree_x - camera.x), int(tree_y - camera.y))
                    pygame.draw.circle(surface, (39, 61, 49), center, 13)
                    pygame.draw.circle(surface, (74, 91, 65), center, 8)

        # Three offset towers give the financial district a readable skyline.
        for x, y, width, height in ((2070, 205, 82, 235), (2190, 95, 105, 350),
                                    (2330, 260, 76, 220), (2785, 330, 185, 295)):
            tower = rect_at(x, y, width, height)
            pygame.draw.rect(surface, (64, 76, 79), tower)
            pygame.draw.rect(surface, (123, 127, 116), tower, 2)
            for window_y in range(tower.y + 12, tower.bottom - 10, 22):
                for window_x in range(tower.x + 10, tower.right - 6, 17):
                    pygame.draw.rect(surface, (164, 155, 121), (window_x, window_y, 6, 9))

        civic = rect_at(2240, 520, 205, 125)
        pygame.draw.rect(surface, (118, 112, 96), civic)
        pygame.draw.polygon(surface, (153, 143, 117),
                            [(civic.x - 8, civic.y + 26), (civic.centerx, civic.y),
                             (civic.right + 8, civic.y + 26)])
        for pillar_x in range(civic.x + 20, civic.right - 10, 36):
            pygame.draw.rect(surface, (183, 168, 133), (pillar_x, civic.y + 34, 8, 77))

        subway = rect_at(2070, 1170, 125, 72)
        pygame.draw.rect(surface, (34, 42, 43), subway)
        pygame.draw.rect(surface, (151, 131, 97), subway, 2)
        for stair_y in range(subway.y + 13, subway.bottom - 8, 9):
            pygame.draw.line(surface, (139, 143, 131), (subway.x + 12, stair_y),
                             (subway.right - 12, stair_y), 2)
        pygame.draw.line(surface, (151, 131, 97), (subway.x + 7, subway.y + 7),
                         (subway.x + 7, subway.bottom - 5), 3)

        factory = rect_at(3650, 1800, 255, 185)
        pygame.draw.rect(surface, (78, 81, 75), factory)
        pygame.draw.polygon(surface, (109, 105, 89),
                            [(factory.x, factory.y + 25), (factory.x + 50, factory.y),
                             (factory.x + 105, factory.y + 25), (factory.x + 160, factory.y),
                             (factory.right, factory.y + 25), (factory.right, factory.y + 38),
                             (factory.x, factory.y + 38)])
        for stack_x in (factory.x + 35, factory.x + 190):
            pygame.draw.rect(surface, (74, 75, 68), (stack_x, factory.y - 78, 18, 80))
        for door_x in range(factory.x + 16, factory.right - 30, 53):
            pygame.draw.rect(surface, (43, 50, 49), (door_x, factory.bottom - 58, 34, 54))

        scrapyard = rect_at(680, 760, 240, 135)
        pygame.draw.rect(surface, (62, 65, 58), scrapyard)
        for car_x, car_y, color in ((18, 20, (113, 86, 71)), (90, 36, (83, 99, 101)),
                                    (151, 17, (130, 116, 80)), (66, 88, (102, 79, 72)),
                                    (174, 83, (76, 93, 83))):
            pygame.draw.rect(surface, color, (scrapyard.x + car_x, scrapyard.y + car_y, 38, 20))