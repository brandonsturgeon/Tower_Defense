from pygame import sprite, Surface, Rect
from tower_frame import TowerFrame
from projectile import Projectile
import time

class Tower(sprite.Sprite):
    """ Base Tower Class """
    def __init__(self, pos):
        sprite.Sprite.__init__(self)

        self.name = "Tower"
        self.pos = pos
        self.grid_pos = tuple([x/40 for x in self.pos])
        self.image = Surface((40, 40)).convert()
        self.kills = 0
        self.damage_done = 0
        self.image.fill((225, 50, 50))
        self.rect = Rect(self.pos, self.image.get_size())
        self.projectile = Surface((10, 10)).convert()
        self.projectile.fill((0, 255, 255))
        self.projectile_speed = 5
        self.projectiles = sprite.Group()
        self.turn_yield = 0

        self.radius = 200
        self.fire_rate = 1
        self.damage = 25
        self.level = 1
        self.upgrade_cost = 5
        self.description = "A basic tower with moderate fire speed and damage."
        self.cost = 25
        self.value = self.cost

        self.target = None
        self.last_shot = time.time()

        self.image.convert()
        self.projectile.convert()
        self.frame = TowerFrame(self)

    def update(self, monsters, screen, screen_rect):

        # If there is no target
        if self.target is None:
            for monster in monsters:
                if monster.can_move:
                    if sprite.collide_circle(monster, self):
                        self.target = monster
                        break

        # Shoot at the target
        if self.target is not None:
            # If the target has gone out of range
            if not sprite.collide_circle(self.target, self):
                self.target = None
            else:
                self.shoot()
                if self.target.health <= 0:
                    self.target = None

        self.projectiles.update(monsters, screen_rect)
        self.projectiles.draw(screen)

    def update_info(self):
        self.frame = TowerFrame(self)

    def shoot(self):
        if time.time() - self.last_shot >= self.fire_rate:
            self.projectiles.add(Projectile(pos=(self.rect.x, self.rect.y),
                                            tower=self,
                                            target=self.target,
                                            image=self.projectile,
                                            speed=self.projectile_speed,
                                            damage=self.damage))
            self.last_shot = time.time()

    def upgrade(self):
        if self.level < 5:
            self.damage += 5
            self.projectile_speed -= 0.5
            self.level += 1
            self.update_info()
            return True
        return False

