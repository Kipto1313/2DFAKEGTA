# Fallen Streets

An original top-down urban crime-drama prototype set in Ashport City. The city, characters, and story are original; all visuals are drawn at runtime, so no external art assets are needed.

## Run

```bash
python -m pip install -r requirements.txt
python main.py
```

Use `python main.py --headless` for a short startup smoke test (requires a working SDL video driver; CI can set `SDL_VIDEODRIVER=dummy`).

## Controls

- `WASD`: move, `Shift`: sprint, `Space`: dodge
- Mouse: aim, left click: fire, `R`: reload
- `1`-`6`: select a weapon, `E`: enter or leave a vehicle
- `F`: interact with the current mission objective, `F5`: save, `F9`: load
- `Esc`: quit

The prototype includes a scrollable procedural city, five mission arcs and the final choice, combat, enemy investigation/pursuit, traffic, drivable cars, wanted response, weather and a day/night cycle. Campaign features are intentionally presented as a playable foundation with placeholder art and simplified simulation.