"""Runtime placeholder assets for a game that ships without binary art files."""

import pygame


class AssetManager:
    """Creates and caches simple drawn surfaces and fonts."""

    def __init__(self):
        self.fonts = {}
        self.surfaces = {}

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = pygame.font.SysFont("dejavusans", size, bold=bold)
        return self.fonts[key]

    def placeholder(self, key, size, fill, border=(18, 23, 25)):
        if key not in self.surfaces:
            image = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(image, fill, image.get_rect(), border_radius=3)
            pygame.draw.rect(image, border, image.get_rect(), 2, border_radius=3)
            self.surfaces[key] = image
        return self.surfaces[key]


ASSETS = AssetManager()