"""JSON save/load for player progression and owned vehicles."""

import json
from pathlib import Path


SAVE_PATH = Path(__file__).with_name("fallen_streets_save.json")


def save_game(player, missions, vehicles, path=SAVE_PATH):
    data = {
        "player": {"x": player.x, "y": player.y, "health": player.health,
                   "armor": player.armor, "cash": player.cash, "reputation": player.reputation,
                   "inventory": player.inventory, "weapons": sorted(player.unlocked),
                   "selected_weapon": player.weapon.spec.name,
                   "weapon_ammo": {name: {"ammo": weapon.ammo, "reserve": weapon.reserve}
                                   for name, weapon in player.weapons.items()}},
        "missions": missions.to_dict(),
        "owned_vehicles": [vehicle.kind for vehicle in vehicles if not vehicle.traffic],
    }
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_game(player, missions, vehicles=None, path=SAVE_PATH):
    source = Path(path)
    if not source.exists():
        return False
    data = json.loads(source.read_text(encoding="utf-8"))
    saved = data.get("player", {})
    for field in ("x", "y", "health", "armor", "cash", "reputation"):
        if field in saved:
            setattr(player, field, saved[field])
    player.inventory = saved.get("inventory", player.inventory)
    player.unlocked = set(saved.get("weapons", ["Pistol"]))
    selected_weapon = saved.get("selected_weapon", "Pistol")
    if selected_weapon in player.unlocked:
        from weapons import SPECS
        selected_index = next((index for index, spec in enumerate(SPECS)
                               if spec.name == selected_weapon), None)
        if selected_index is not None:
            player.select_weapon(selected_index)
    for name, ammo in saved.get("weapon_ammo", {}).items():
        if name in player.weapons:
            player.weapons[name].ammo = ammo.get("ammo", player.weapons[name].ammo)
            player.weapons[name].reserve = ammo.get("reserve", player.weapons[name].reserve)
    missions.load_dict(data.get("missions", {}))
    if vehicles is not None:
        from vehicle import Vehicle
        traffic = [vehicle for vehicle in vehicles if vehicle.traffic]
        owned = [Vehicle(player.x + 45 + index * 50, player.y + 45, kind)
                 for index, kind in enumerate(data.get("owned_vehicles", []))]
        vehicles[:] = traffic + owned
    return True