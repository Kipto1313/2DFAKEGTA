"""Fallen Streets: playable top-down Ashport City prototype."""

import argparse
import os


def run():
    parser = argparse.ArgumentParser(description="Fallen Streets: Ashport City")
    parser.add_argument("--headless", action="store_true", help="run a brief startup smoke test")
    args = parser.parse_args()
    if args.headless:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    import pygame
    from save_system import load_game, save_game
    from ui import GameUI
    from world import GameWorld

    pygame.init()
    pygame.display.set_caption("Fallen Streets | Ashport City")
    size = (1180, 760)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    ui = GameUI(size)
    world = GameWorld(*size)
    running = True
    smoke_frames = 4 if args.headless else None
    frames = 0

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    world.player.dodge(pygame.key.get_pressed())
                elif event.key == pygame.K_e:
                    world.toggle_vehicle()
                elif event.key == pygame.K_f:
                    world.interact()
                elif event.key == pygame.K_r:
                    world.player.weapon.reload()
                elif event.key == pygame.K_F5:
                    save_game(world.player, world.missions, world.vehicles)
                    world.notify("ASHPORT PROGRESS SAVED")
                elif event.key == pygame.K_F9:
                    if load_game(world.player, world.missions, world.vehicles):
                        world.notify("SAVE FILE LOADED")
                    else:
                        world.notify("NO SAVE FILE FOUND")
                elif event.key in (pygame.K_j, pygame.K_v) and world.missions.complete:
                    choice = "JUSTICE" if event.key == pygame.K_j else "REVENGE"
                    world.ending = world.missions.choose(choice, world.player) or ""
                    world.notify(world.ending, 8)
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    world.player.select_weapon(event.key - pygame.K_1)

        keys = pygame.key.get_pressed()
        world.update(dt, keys, pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])
        world.draw(screen, ui)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, (231, 211, 171), (mouse_x, mouse_y), 7, 1)
        pygame.draw.line(screen, (231, 211, 171), (mouse_x - 11, mouse_y), (mouse_x - 5, mouse_y), 1)
        pygame.draw.line(screen, (231, 211, 171), (mouse_x + 5, mouse_y), (mouse_x + 11, mouse_y), 1)
        pygame.display.flip()
        frames += 1
        if smoke_frames is not None and frames >= smoke_frames:
            running = False

    pygame.quit()


if __name__ == "__main__":
    run()