from pygame import sprite
from tower import Tower
from tower_frame import TowerFrame
from projectile import Projectile
import time

class MultiShot(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Multi Shot Tower"
        self.image.fill((150, 0, 150))
        self.fire_rate = 1.5
        self.damage = 20
        self.radius = 150
        self.max_targets = 3
        self.description = "A tower which hits multiple enemy units."
        self.cost = 125
        self.target = []
        self.extra_attributes = {"Max Targets": str(self.max_targets)}
        self.frame = TowerFrame(self, self.extra_attributes)

    def update(self, monsters, screen, screen_rect):
        self.target = []

        # Gets nearby targets
        for monster in monsters:
            if len(self.target) == 5:
                break
            elif sprite.collide_circle(monster, self):
                self.target.append(monster)
        if len(self.target) > 0:
            self.shoot()

        self.projectiles.update(monsters, screen_rect)
        self.projectiles.draw(screen)

    def update_info(self):
        self.extra_attributes = {"Max Targets": str(self.max_targets)}
        self.frame = TowerFrame(self, self.extra_attributes)

    def shoot(self):
        if time.time() - self.last_shot >= self.fire_rate:
            for t in self.target:
                self.projectiles.add(Projectile(pos=(self.rect.x, self.rect.y),
                                                tower=self,
                                                target=t,
                                                image=self.projectile,
                                                speed=self.projectile_speed,
                                                damage=self.damage))
            self.last_shot = time.time()

    def upgrade(self):
        if self.level < 5:
            self.damage += 5
            if self.max_targets < 5:
                self.max_targets += 1
            self.radius += 5
            self.level += 1
            self.update_info()
            return True
        return False
class MultiShot(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Multi Shot Tower"
        self.image.fill((150, 0, 150))
        self.fire_rate = 1.5
        self.damage = 20
        self.radius = 150
        self.max_targets = 3
        self.description = "A tower which hits multiple enemy units."
        self.cost = 125
        self.target = []
        self.extra_attributes = {"Max Targets": str(self.max_targets)}
        self.frame = TowerFrame(self, self.extra_attributes)

    def update(self, monsters, screen, screen_rect):
        self.target = []

        # Gets nearby targets
        for monster in monsters:
            if len(self.target) == 5:
                break
            elif sprite.collide_circle(monster, self):
                self.target.append(monster)
        if len(self.target) > 0:
            self.shoot()

        self.projectiles.update(monsters, screen_rect)
        self.projectiles.draw(screen)

    def update_info(self):
        self.extra_attributes = {"Max Targets": str(self.max_targets)}
        self.frame = TowerFrame(self, self.extra_attributes)

    def shoot(self):
        if time.time() - self.last_shot >= self.fire_rate:
            for t in self.target:
                self.projectiles.add(Projectile(pos=(self.rect.x, self.rect.y),
                                                tower=self,
                                                target=t,
                                                image=self.projectile,
                                                speed=self.projectile_speed,
                                                damage=self.damage))
            self.last_shot = time.time()

    def upgrade(self):
        if self.level < 5:
            self.damage += 5
            if self.max_targets < 5:
                self.max_targets += 1
            self.radius += 5
            self.level += 1
            self.update_info()
            return True
        return False
