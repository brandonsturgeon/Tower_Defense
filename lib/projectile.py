from pygame import sprite, Rect
from math import atan2, cos, sin, hypot

# Base Projectile class
class Projectile(sprite.Sprite):
    def __init__(self, pos, tower, target, image, speed, damage):
        sprite.Sprite.__init__(self)
        self.pos = pos
        self.tower = tower
        self.target = target
        self.image = image
        self.speed = speed
        self.damage = damage
        self.rect = Rect(self.pos, self.image.get_size())

        self.angle = atan2((self.target.rect.centery-self.rect.centery),
                                (self.target.rect.centerx-self.rect.centerx))
        self.x_speed = cos(self.angle)*self.speed
        self.y_speed = sin(self.angle)*self.speed

    def update(self, monsters, screen):

        # Kills the projectile if it doesn't get there before the target dies
        if self.target is None:
            self.kill()
            return

        # Calculates where the projectile needs to go
        self.angle = atan2((self.target.rect.centery-self.rect.centery),
                                (self.target.rect.centerx-self.rect.centerx))

        distance = hypot(self.target.rect.centerx - self.rect.centerx,
                              self.target.rect.centery - self.rect.centery)
        mod = self.target.speed+1
        # Calculates the X and Y speed
        xspeed, yspeed = cos(self.angle)*mod, sin(self.angle)*mod
        self.x_speed = xspeed + xspeed/abs(xspeed) if xspeed != 0 else 0
        self.y_speed = yspeed + yspeed/abs(yspeed) if yspeed != 0 else 0

        # If the projectile is within range, it hit the target
        if abs(self.rect.centerx - self.target.rect.centerx) <= 20:
            if abs(self.rect.centery - self.target.rect.centery) <= 20:
                self.do_damage(monsters)
                self.kill()
            else:
                self.rect.move_ip((self.x_speed, self.y_speed))
        else:
            self.rect.move_ip((self.x_speed, self.y_speed))

        # Destroys the projectile if it goes off screen
        if not screen.contains(self.rect):
            self.kill()

    def do_damage(self, monsters):
        for monster in monsters:
            # Does damage to the target, and adds kills and money rewards if it dies, also adds damage_done to tower
            if monster == self.target:
                # dmg_result returns (None/Value of monster, Damage done by projectile)
                dmg_result = monster.damage(self.damage)
                if dmg_result[0] is not None:
                    self.tower.kills += 1
                    self.tower.turn_yield += dmg_result[0]
                self.tower.damage_done += dmg_result[1]
                break
