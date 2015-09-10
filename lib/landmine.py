from pygame import sprite
from tower import Tower
from tower_frame import TowerFrame

class LandMine(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Landmine"
        self.image.fill((50, 50, 50))
        self.fire_rate = 0.25
        self.damage = 75
        self.description = "A simple, single-use landmine."
        self.cost = 10

        self.frame = TowerFrame(self)

    def update(self, monsters, screen, screen_rect):
        for monster in monsters:
            if self.rect.colliderect(monster.rect):
                self.effect(monster, monsters)

    def update_info(self):
        self.frame = TowerFrame(self)

    def effect(self, target, monsters):
        for monster in monsters:
            if sprite.collide_circle(target, monster):
                monster.damage(self.damage)
        self.kill()

    def upgrade(self):
        if self.level < 5:
            self.damage += 20
            self.upgrade_cost += 5
            self.level += 1
            self.update_info()
            return True
        return False
