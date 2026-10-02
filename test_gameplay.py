"""Regression tests for player, NPC, and death behavior."""

import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from enemy import Enemy
from player import Player
from ui import GameUI
from world import GameWorld


class GameplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1180, 760))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_neutral_enemy_does_not_attack_on_proximity(self):
        enemy = Enemy(0, 0)
        shots = []

        enemy.update(.05, SimpleNamespace(x=100, y=0), shots, [])

        self.assertEqual(enemy.state, "patrol")
        self.assertEqual(shots, [])

    def test_attacked_enemy_becomes_hostile(self):
        enemy = Enemy(0, 0)
        enemy.damage(1)

        enemy.update(.05, SimpleNamespace(x=100, y=0), [], [])

        self.assertTrue(enemy.angered)
        self.assertEqual(enemy.state, "alert")

    def test_player_starts_with_fists_and_can_select_pistol(self):
        player = Player(0, 0)

        self.assertEqual(player.weapon.spec.name, "Fists")
        player.select_weapon(1)
        self.assertEqual(player.weapon.spec.name, "Pistol")

    def test_fists_hit_an_enemy_in_front_of_player(self):
        world = GameWorld(1180, 760)
        world.enemies = [Enemy(world.player.x + 30, world.player.y)]
        initial_health = world.enemies[0].health

        world.fire((world.player.x + 100, world.player.y))

        self.assertLess(world.enemies[0].health, initial_health)
        self.assertTrue(world.enemies[0].angered)

    def test_zero_health_shows_wasted_state_and_freezes_game(self):
        world = GameWorld(1180, 760)
        world.player.take_damage(1000)
        world._update_projectiles(0)
        initial_position = (world.player.x, world.player.y)

        self.assertTrue(world.game_over)
        world.update(1, pygame.key.get_pressed(), (0, 0), True)
        self.assertEqual((world.player.x, world.player.y), initial_position)

        world.draw(self.screen, GameUI(self.screen.get_size()))


if __name__ == "__main__":
    unittest.main()
