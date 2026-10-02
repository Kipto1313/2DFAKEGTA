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
- Mouse: aim, left click: punch with fists or fire an equipped gun, `R`: reload
- `1`-`7`: select fists or a weapon, `E`: enter or leave a vehicle
- `Enter`: restart after being wasted
- `F`: interact with the current mission objective, `F5`: save, `F9`: load
- `Esc`: quit

The prototype includes a scrollable procedural city, a circular street minimap with the current mission marked `M`, five mission arcs and the final choice, combat, enemy investigation/pursuit, traffic, drivable cars, wanted response, weather and a day/night cycle. Most city NPCs are neutral until attacked; aggressive NPCs and police can fight back when provoked. Reaching zero health displays the `WASTED` screen. Campaign features are intentionally presented as a playable foundation with placeholder art and simplified simulation.