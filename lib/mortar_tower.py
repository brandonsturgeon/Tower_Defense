from pygame import Surface
from tower import Tower
from tower_frame import TowerFrame

class MortarTower(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Mortar Tower"
        self.image = Surface((40, 40)).convert()
        self.image.fill((0, 0, 255))
        self.projectile = Surface((15, 15)).convert()
        self.projectile.fill((255, 150, 0))
        self.projectile_speed = 3

        self.radius = 300
        self.fire_rate = 3
        self.damage = 15
        self.description = "A long-range tower that fires mortars which " \
                           "explode on impact, dealing damage to all nearby enemies."
        self.cost = 75

        self.frame = TowerFrame(self)

    def update_info(self):
        self.frame = TowerFrame(self)

    def upgrade(self):
        if self.level < 5:
            self.damage += 5
            self.radius += 10
            self.projectile_speed += 0.25
            self.level += 1
            self.update_info()
            return True
        return False


