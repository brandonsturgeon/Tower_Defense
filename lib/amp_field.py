from tower import Tower
from tower_frame import TowerFrame

class AmpField(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Amp Field"
        self.image.fill((255, 255, 0))
        self.fire_rate = 0
        self.damage = 0
        self.radius = 20
        self.damage_mod = 1.5
        self.description = "A block which increases the damage taken by all enemies on it."
        self.cost = 25
        self.extra_attributes = {"Damage Amp: ": str((self.damage_mod-1) * 100) + "%"}
        self.frame = TowerFrame(self, self.extra_attributes)

    def update(self, monsters, screen, screen_rect):
        for monster in monsters:
            if self.rect.colliderect(monster.rect):
                self.effect(monster)

    def update_info(self):
        self.extra_attributes = {"Damage Amp: ": str((self.damage_mod-1) * 100) + "%"}
        self.frame = TowerFrame(self, self.extra_attributes)

    @staticmethod
    def effect(target):
        target.damage_mod = 1.5

    def upgrade(self):
        if self.level < 5:
            self.damage_mod += 0.5
            self.upgrade_cost += 5
            self.level += 1
            self.update_info()
            return True
        return False

