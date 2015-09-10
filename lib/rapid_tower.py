from pygame import Surface
from tower import Tower
from tower_frame import TowerFrame

class RapidTower(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Rapid-fire Tower"
        self.image.fill((120, 0, 255))
        self.projectile = Surface((5, 5)).convert()
        self.projectile.fill((120, 0, 255))
        self.projectile_speed = 10
        self.fire_rate = 0.25
        self.damage = 7
        self.description = "A tower with moderate range and very quick attack speed."
        self.cost = 50

        self.frame = TowerFrame(self)

    def update_info(self):
        self.frame = TowerFrame(self)

    def upgrade(self):
        if self.level < 5:
            self.damage += 1
            self.fire_rate -= 0.025
            self.level += 1
            self.update_info()
            return True
        return False

