"""Mission objectives, checkpoints, unlocks, and ending choices."""

from enemy import Enemy


MISSIONS = [
    ("THE FUNERAL", "Ethan returns to Ashport after his brother Marcus is murdered.", [
        ("Drive to the cemetery", (980, 2830)), ("Attend the funeral", (980, 2830)),
        ("Meet Marcus' friends", (1040, 2790)), ("Visit Marcus' apartment", (695, 2440)),
        ("Search the apartment", (695, 2440)), ("Escape the masked gunmen", (510, 2320)),
    ]),
    ("MISSING WITNESS", "Investigative journalist Sarah Reed has disappeared.", [
        ("Locate Sarah", (1820, 2110)), ("Travel to the warehouse district", (3410, 2250)),
        ("Investigate the clues", (3580, 2460)), ("Fight through the gang", (3635, 2510)),
        ("Rescue Sarah", (3515, 2410)),
    ]),
    ("GHOSTS OF THE HARBOR", "Marcus uncovered illegal shipments entering Ashport.", [
        ("Follow the cargo truck", (3470, 2090)), ("Remain undetected", (3620, 2260)),
        ("Infiltrate the harbor", (3780, 2380)), ("Photograph the evidence", (3950, 2500)),
        ("Escape the harbor gunfight", (3240, 2130)),
    ]),
    ("THE MAYOR'S SHADOW", "The evidence reaches into Ashport's city government.", [
        ("Escape the police", (2340, 640)), ("Reach the safehouse", (695, 2440)),
        ("Destroy the false evidence", (695, 2440)), ("Meet your allies", (1050, 2480)),
    ]),
    ("NO HEROES", "Victor Hale is preparing to flee the city.", [
        ("Assault Hale Tower", (2860, 470)), ("Fight through private security", (2860, 470)),
        ("Reach the penthouse", (2900, 430)), ("Confront Victor Hale", (2900, 430)),
        ("Record Victor's confession", (2900, 430)),
    ]),
]


class MissionManager:
    def __init__(self):
        self.mission_index = 0
        self.objective_index = 0
        self.complete = False
        self.choice = None
        self.last_checkpoint = 0
        self.banner_time = 5.0
        self.safehouse_unlocked = False
        self.harbor_unlocked = False
        self.armored_vehicles_unlocked = False

    @property
    def mission(self):
        return MISSIONS[min(self.mission_index, len(MISSIONS) - 1)]

    @property
    def objective(self):
        if self.complete:
            return "Choose justice or revenge"
        return self.mission[2][self.objective_index][0]

    @property
    def target(self):
        if self.complete:
            return self.mission[2][-1][1]
        return self.mission[2][self.objective_index][1]

    @property
    def title(self):
        return "ASHPORT CITY" if self.complete else self.mission[0]

    @property
    def story(self):
        return "The city keeps its own counsel." if self.complete else self.mission[1]

    def interact(self, player, enemies):
        if self.complete:
            return {"choice_prompt": True}
        self.objective_index += 1
        self.banner_time = 4.0
        if self.mission_index == 0 and self.objective_index == 5:
            for _ in range(4):
                enemy = Enemy(player.x + 90, player.y + 65, aggressive=True)
                enemy.investigate((player.x, player.y))
                enemies.append(enemy)
        if self.objective_index >= len(self.mission[2]):
            self.objective_index = 0
            completed_index = self.mission_index
            self.mission_index += 1
            self.last_checkpoint = self.mission_index
            if self.mission_index >= len(MISSIONS):
                self.mission_index = len(MISSIONS) - 1
                self.complete = True
            reward = self._reward(player, completed_index)
            self.banner_time = 8.0
            return {"mission_complete": True, "reward": reward}
        return {"advanced": True}

    def choose(self, choice, player):
        if not self.complete or choice not in ("JUSTICE", "REVENGE"):
            return None
        self.choice = choice
        player.reputation += 25 if choice == "JUSTICE" else -10
        return "City begins to recover." if choice == "JUSTICE" else "Truth dies with Victor. Ethan becomes a fugitive."

    def _reward(self, player, completed_index):
        rewards = [
            ("Safehouse unlocked. Pistol and revolver secured.", 500, "Pistol"),
            ("Sarah Reed rescued. SMG unlocked. New district opened.", 900, "SMG"),
            ("Harbor access granted. Weapon cache recovered.", 1250, "Shotgun"),
            ("Armored vehicles and advanced weapons unlocked.", 1800, "Carbine"),
            ("Ashport's last secret is yours to decide.", 3000, "Sniper"),
        ]
        message, cash, weapon = rewards[completed_index]
        player.cash += cash
        player.unlock_weapon(weapon)
        player.reputation += 8
        if completed_index == 0:
            self.safehouse_unlocked = True
            player.unlock_weapon("Revolver")
        elif completed_index == 2:
            self.harbor_unlocked = True
        elif completed_index == 3:
            self.armored_vehicles_unlocked = True
        return message

    def to_dict(self):
        return {"mission_index": self.mission_index, "objective_index": self.objective_index,
            "complete": self.complete, "choice": self.choice, "last_checkpoint": self.last_checkpoint,
            "safehouse_unlocked": self.safehouse_unlocked, "harbor_unlocked": self.harbor_unlocked,
            "armored_vehicles_unlocked": self.armored_vehicles_unlocked}

    def load_dict(self, data):
        self.mission_index = max(0, min(len(MISSIONS) - 1, int(data.get("mission_index", 0))))
        self.objective_index = max(0, min(len(self.mission[2]) - 1, int(data.get("objective_index", 0))))
        self.complete = bool(data.get("complete", False))
        self.choice = data.get("choice")
        self.last_checkpoint = int(data.get("last_checkpoint", 0))
        self.safehouse_unlocked = bool(data.get("safehouse_unlocked", False))
        self.harbor_unlocked = bool(data.get("harbor_unlocked", False))
        self.armored_vehicles_unlocked = bool(data.get("armored_vehicles_unlocked", False))