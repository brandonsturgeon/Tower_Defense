from pygame import sprite
from tower import Tower
from tower_frame import TowerFrame

class SlowTower(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Slow Tower"
        self.image.fill((255, 170, 0))
        self.fire_rate = 0
        self.damage = 0
        self.radius = 50
        self.speed_mod = 0.75
        self.description = "A tower which slows all enemies in its radius."
        self.cost = 75
        self.extra_attributes = {"Slow Amount: ": str((1-self.speed_mod) * 100) + "%"}
        self.frame = TowerFrame(self, self.extra_attributes)

    def update(self, monsters, screen, screen_rect):
        for monster in monsters:
            if sprite.collide_circle(self, monster):
                monster.speed_mod = self.speed_mod

    def update_info(self):
        self.extra_attributes = {"Slow Amount: ": str((1-self.speed_mod) * 100) + "%"}
        self.frame = TowerFrame(self, self.extra_attributes)

    def upgrade(self):
        if self.level < 5:
            self.speed_mod -= 0.15
            self.radius += 5
            self.level += 1
            self.update_info()
            return True
        return False
