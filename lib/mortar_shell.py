from pygame import sprite
from projectile import Projectile

class MortarShell(Projectile):
    """ Explodes on impact dealing damage in 50 radius """
    def __init__(self, pos, target, image, speed, damage):
        Projectile.__init__(self, pos, target, image, speed, damage)
        self.radius = 50

    def do_damage(self, monsters):
        for monster in monsters:
            if sprite.collide_circle(self, monster):
                dmg_result = monster.damage(self.damage)
                if dmg_result[0] is not None:
                    self.tower.kills += 1
                    self.tower.turn_yield += dmg_result[0]
                self.tower.damage_done += dmg_result[1]


