# Pygame Tower Defense
# Brandon Sturgeon


import pygame
import random
import time
import math


class OutlinedSurface():
    def __init__(self, surface, offset, bgcolor=(255, 255, 255)):
        self.inside_surface = surface
        self.offset = offset
        self.bgcolor = bgcolor

        self.surface = pygame.Surface((self.inside_surface.get_width() + offset*2,
                                       self.inside_surface.get_height() + offset*2)).convert()
        self.surface.fill(self.bgcolor)
        self.surface.blit(self.inside_surface, (offset, offset))


class Block(pygame.sprite.Sprite):
    def __init__(self, pos, is_end):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.grid_pos = tuple([x/40 for x in self.pos])
        self.image = pygame.Surface((40, 40)).convert()
        self.color = (125, 125, 125)
        self.image.fill((255, 255, 255))
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        self.is_shown = False
        self.is_path = False
        self.neighbors = set()
        self.path_value = 0
        self.is_end = is_end

    def get_neighbors(self, lst):
        for b in lst:
            if self in b:
                a = self

                # Left
                if b.index(a) != 0:
                    to_add = b[b.index(a)-1]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(b[b.index(a)-1])

                # Right
                if b.index(a) != len(b)-1:
                    to_add = b[b.index(a)+1]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(b[b.index(a)+1])

                # Above
                if lst.index(b) != 0:
                    to_add = lst[lst.index(b)-1][b.index(a)]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(lst[lst.index(b)-1][b.index(a)])

                # Below
                if lst.index(b) != len(lst)-1:
                    to_add = lst[lst.index(b)+1][b.index(a)]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(lst[lst.index(b)+1][b.index(a)])


# Base Monster class
class Monster(pygame.sprite.Sprite):
    def __init__(self, move_time, nodes):
        pygame.sprite.Sprite.__init__(self)
        self.nodes = nodes
        self.orig_nodes = nodes
        self.move_time = move_time
        self.spawn_time = time.time()
        self.image = pygame.Surface((40, 40)).convert()
        self.image_inside = pygame.Surface((38, 38)).convert()
        self.image_inside.fill((0, 255, 0))
        self.image.blit(self.image_inside, (1, 1))
        self.pos = (80, 40)
        self.real_pos = (80, 40)
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        self.speed = 2
        self.speed_mod = 1
        self.diag_speed = 2
        self.target_pos = (880, 560)
        self.value = 1
        self.cost = 0
        self.health = 100
        self.damage_mod = 1
        self.counter = 0
        self.cur_node = self.nodes[0]
        self.the_dir = (0, 0)
        self.can_move = False

        self.name = "Monster"
        self.description = "A basic monster with slow movement speed and moderate health."

    def update(self, window):

        if time.time() - self.spawn_time >= self.move_time:
            self.can_move = True
            # If it's hit the last block
            if len(self.nodes) < 1:
                self.kill()
                return self.value
            else:

                # Figuring direction
                if self.nodes[0].rect.x > self.cur_node.rect.x:
                    self.the_dir = (1, 0)
                elif self.nodes[0].rect.x < self.cur_node.rect.x:
                    self.the_dir = (-1, 0)
                elif self.nodes[0].rect.y > self.cur_node.rect.y:
                    self.the_dir = (0, 1)
                elif self.nodes[0].rect.y < self.cur_node.rect.y:
                    self.the_dir = (0, -1)

                # Check to see the most the monster can move
                for speed in range(0, self.speed+1):
                    t_dir = tuple([x * speed * self.speed_mod for x in self.the_dir])

                    # Monster can only move this much
                    if self.rect.move(t_dir) == self.nodes[0].rect:
                        self.rect.move_ip(t_dir)
                        self.real_pos = tuple(map(sum, zip(self.real_pos, t_dir)))
                        self.cur_node = self.nodes.pop(0)
                        break
                else:
                    # The monster can move by self.speed
                    a = tuple([x * self.speed * self.speed_mod for x in self.the_dir])
                    self.real_pos = tuple(map(sum, zip(self.real_pos, a)))
                    self.pos = tuple(map(round, self.real_pos))
                    self.rect.x, self.rect.y = self.pos

                # Conditions for the monster to die
                die_conditions = [self.rect.top >= window.get_height(),
                                  self.rect.left >= window.get_width(),
                                  self.rect.bottom <= 0]
                if any(die_conditions):
                    self.kill()
                    return self.value

                # Resetting the modifiers, they'll be changed if the monster is under an effect
                self.speed_mod = 1
                self.damage_mod = 1
        return 0

    # Does damage to the monster and checks if it dies
    def damage(self, damage):
        self.health -= damage*self.damage_mod

        # Returns the amount of money to grant the player if the monster dies and also how much damage was done
        if self.health <= 0:
            self.kill()
            return self.value, damage*self.damage_mod
        else:
            return None, damage*self.damage_mod


class FastMonster(Monster):
    def __init__(self, move_time, nodes):
        Monster.__init__(self, move_time, nodes)
        self.image = pygame.Surface((20, 20)).convert()
        self.image_inside = pygame.Surface((18, 18)).convert()
        self.image_inside.fill((255, 255, 0))
        self.image.blit(self.image_inside, (1, 1))
        self.rect = pygame.Rect(self.pos, (40, 40))
        self.speed = 4
        self.diag_speed = 3
        self.value = 0.5
        self.health = 50

        self.name = "Fast Monster"
        self.description = "A small monster with very quick movement speed, but low health."

class ArmorMonster(Monster):
  def __init__(self, move_time, nodes):
    Monster.__init__(self, move_time, nodes)
    self.image_inside.fill((142, 163, 12))
    self.image.blit(self.image_inside, (1, 1))
    self.rect = pygame.Rect(self.pos, (40, 40))
    self.speed = 1
    self.diag_speed = 3
    self.value = 10
    self.health = 100
    self.armor = 500

    self.name = "Armored Monster"
    self.description = "An armored monster that takes progressively more damage as it is hit"

  # Does damage to the monster and checks if it dies
  def damage(self, damage):
    if self.armor > 0:
      self.armor -= 25
    else:
      self.health -= damage*self.damage_mod

    # Returns the amount of money to grant the player if the monster dies and also how much damage was done
    if self.health <= 0:
        self.kill()
        return self.value, damage*self.damage_mod
    else:
        return None, damage*self.damage_mod


# Base Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, tower, target, image, speed, damage):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.tower = tower
        self.target = target
        self.image = image
        self.speed = speed
        self.damage = damage
        self.rect = pygame.Rect(self.pos, self.image.get_size())

        self.angle = math.atan2((self.target.rect.centery-self.rect.centery),
                                (self.target.rect.centerx-self.rect.centerx))
        self.x_speed = math.cos(self.angle)*self.speed
        self.y_speed = math.sin(self.angle)*self.speed

    def update(self, monsters, screen):

        # Kills the projectile if it doesn't get there before the target dies
        if self.target is None:
            self.kill()
            return

        # Calculates where the projectile needs to go
        self.angle = math.atan2((self.target.rect.centery-self.rect.centery),
                                (self.target.rect.centerx-self.rect.centerx))

        distance = math.hypot(self.target.rect.centerx - self.rect.centerx,
                              self.target.rect.centery - self.rect.centery)
        mod = self.target.speed+1
        # Calculates the X and Y speed
        xspeed, yspeed = math.cos(self.angle)*mod, math.sin(self.angle)*mod
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


# Explodes on impact dealing damage in 50 radius
class MortarShell(Projectile):
    def __init__(self, pos, target, image, speed, damage):
        Projectile.__init__(self, pos, target, image, speed, damage)
        self.radius = 50

    def do_damage(self, monsters):
        for monster in monsters:
            if pygame.sprite.collide_circle(self, monster):
                dmg_result = monster.damage(self.damage)
                if dmg_result[0] is not None:
                    self.tower.kills += 1
                    self.tower.turn_yield += dmg_result[0]
                self.tower.damage_done += dmg_result[1]


# Creates a frame full of information for the selected tower
class TowerFrame():
    def __init__(self, tower, extra_attributes=None):
        self.tower = tower
        self.image = pygame.Surface((200, 300)).convert()
        self.image.fill((200, 115, 0))
        self.s_width = self.image.get_width()
        self.s_height = self.image.get_height()

        # Can't divide by 0
        if self.tower.fire_rate == 0:
            dps_calc = 0
        else:
            dps_calc = self.tower.damage/self.tower.fire_rate

        tower_attributes = {"Name": self.tower.name,
                            "Fire Rate": self.tower.fire_rate,
                            "Damage": self.tower.damage,
                            "DPS": dps_calc,
                            "Damage Done": self.tower.damage_done}
        if extra_attributes is None:
            extra_attributes = dict()
        self.t_attributes = dict(tower_attributes.items() + extra_attributes.items())

        # Upgrades
        self.font = pygame.font.Font(None, 18)
        self.upgrade_button = pygame.Surface((100, 50))
        self.upgrade_button.fill((0, 255, 0))
        self.upgrade_button.blit(self.font.render("Upgrade", 1, (0, 0, 0)),
                                 (self.upgrade_button.get_width()/2 - self.font.size("Upgrade")[0]/2,
                                  self.upgrade_button.get_height()/2 - self.font.size("Upgrade")[1]/2))
        self.image.blit(self.upgrade_button, (self.image.get_width() - self.upgrade_button.get_width(),
                                              self.image.get_height() - self.upgrade_button.get_height()))

        level_text = "Level: " + str(self.tower.level)
        self.image.blit(self.font.render(level_text, 1, (0, 0, 0)),
                       (self.image.get_width() - self.upgrade_button.get_width(),
                        self.image.get_height() - self.upgrade_button.get_height() - self.font.size(level_text)[1]))
        self.image.blit(self.tower.image, (self.s_width/2 - self.tower.image.get_width()/2, 2))

        y_value = self.tower.image.get_width() + 7

        # Blits the tower description
        for desc in self.length_splitter(self.font, self.tower.description, self.image.get_width() - 5):
            self.image.blit(self.font.render(desc, 1, (0, 0, 0)), (5, y_value))
            y_value += self.font.get_height() + 1
        y_value += 5

        # Blits the tower's attributes in this order, tacking all extra stuff at the end
        for attr in ["Name", "Fire Rate", "Damage", "DPS", "Damage Done"]+extra_attributes.keys():
            value = self.t_attributes[attr]
            self.image.blit(self.font.render(attr + ": " + str(value), 1, (0, 0, 0)), (5, y_value))
            y_value += self.font.get_height() + 1
        #self.image = OutlinedSurface(self.image, 5).surface

    @staticmethod
    # Used to split text up into lines that will fit the surface
    def length_splitter(font, text, maxlength):
        ret_list = []
        explode = text.split()
        t_str = ""
        while len(explode) > 0:
            if font.size(t_str + explode[0])[0] > maxlength:
                ret_list.append(t_str)
                t_str = ""
            else:
                t_str += explode.pop(0) + " "
                if len(explode) == 0:
                    ret_list.append(t_str)
        return ret_list


# Base Tower Class
class Tower(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)

        self.name = "Tower"
        self.pos = pos
        self.grid_pos = tuple([x/40 for x in self.pos])
        self.image = pygame.Surface((40, 40)).convert()
        self.kills = 0
        self.damage_done = 0
        self.image.fill((255, 0, 0))
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        self.projectile = pygame.Surface((10, 10))
        self.projectile.fill((0, 255, 255))
        self.projectile_speed = 5
        self.projectiles = pygame.sprite.Group()
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
                    if pygame.sprite.collide_circle(monster, self):
                        self.target = monster
                        break

        # Shoot at the target
        if self.target is not None:
            # If the target has gone out of range
            if not pygame.sprite.collide_circle(self.target, self):
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


class MortarTower(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Mortar Tower"
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 0, 255))
        self.projectile = pygame.Surface((15, 15))
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


class RapidTower(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Rapid-fire Tower"
        self.image.fill((120, 0, 255))
        self.projectile = pygame.Surface((5, 5))
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
            if pygame.sprite.collide_circle(self, monster):
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
            elif pygame.sprite.collide_circle(monster, self):
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
            if pygame.sprite.collide_circle(target, monster):
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


# A tab for each tower down at the bottom
class TowerShopTab():
    def __init__(self, tower, pos):
        self.pos = pos
        self.tower = tower
        self.name = self.tower.name
        self.description = self.tower.description
        self.surface_inside = pygame.Surface((123, 38)).convert()
        self.surface_inside.fill((100, 100, 100))
        self.image = tower.image
        self.cost = tower.cost
        self.surface = pygame.Surface((125, 40)).convert()
        self.rect = pygame.Rect(self.pos, self.surface .get_size())
        self.font = pygame.font.Font(None, 15)  
        self.info_tab = tower.frame.image

        self.surface_inside.blit(pygame.transform.scale(self.tower.image, (20, 20)), (5, 10))
        self.surface_inside.blit(self.font.render(self.tower.name, 1, (0, 0, 0)), (30, 25-self.font.get_height()))
        self.surface .blit(self.surface_inside, (1, 1))

    def get_surface(self):
        return self.surface


class InfoTab():
    def __init__(self):
        self.surface_inside = pygame.Surface((295, 128)).convert()
        self.surface = pygame.Surface((300, 130)).convert()

        self.surface_inside.fill((255, 255, 255))
        self.surface.fill((0, 0, 0))
        self.font = pygame.font.Font(None, 15)
        self.l_font = pygame.font.Font(None, 25)

    def update(self, obj=None):
        self.surface_inside.fill((255, 255, 255))
        self.surface.fill((0, 0, 0))
        if obj is not None:
            self.surface_inside.blit(pygame.transform.scale(obj.image, (20, 20)), (5, 5))
            self.surface_inside.blit(self.l_font.render(obj.name, 1, (0, 0, 0)), (30, 25-self.l_font.get_height()))

            cost_str = "$"+str(obj.cost)
            self.surface_inside.blit(self.l_font.render(cost_str, 1, (0, 255, 0)),
                                     (self.surface_inside.get_width() - self.l_font.size(cost_str)[0] - 10, 5))

            y_val = 30
            for line in self.length_splitter(self.font, obj.description, self.surface_inside.get_width()-10):
                self.surface_inside.blit(self.font.render(line, 1, (0, 0, 0)), (5, y_val))
                y_val += self.font.size(line)[1]+5

        self.surface.blit(self.surface_inside, (1, 1))

    # Word-wrap function
    @staticmethod
    def length_splitter(font, text, max_length):
        ret_list = []
        explode = text.split()
        t_str = ""
        while len(explode) > 0:
            if font.size(t_str + explode[0])[0] > max_length:
                ret_list.append(t_str)
                t_str = ""
            else:
                t_str += explode.pop(0) + " "
                if len(explode) == 0:
                    ret_list.append(t_str)
        return ret_list


# Main game class
class Game():
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.game_window = pygame.display.set_mode((1000, 700))
        self.game_window.fill((0, 255, 255))
        self.game_surface = pygame.Surface((1000, 560)).convert()
        self.game_surface_rect = pygame.Rect((0, 0), self.game_surface.get_size())
        self.bottom_bar = pygame.Surface((990, 130)).convert()
        self.bottom_bar.fill((190, 115, 0))
        self.bottom_bar_rect = pygame.Rect((0, 560), (1000, 140))
        self.bottom_bar_outline = pygame.Surface((1000, 140)).convert()
        self.font = pygame.font.Font(None, 26)

        # Creates the game borders, the parts that users can't create a path in
        self.border_list = [pygame.Rect((0, 0), (self.game_surface.get_width(), 40)),
                            pygame.Rect((0, 0), (40, self.game_surface.get_height())),
                            pygame.Rect((0, self.game_surface.get_height()-40), (self.game_surface.get_width(), 40)),
                            pygame.Rect((self.game_surface.get_width()-40, 0), (40, self.game_surface.get_height()))]

        # The bottom box that shows info about what you hover over
        self.info_box = InfoTab()

        #
        self.all_towers = [Tower, MortarTower, RapidTower, LandMine, SlowTower, AmpField, MultiShot]
        self.ground_towers = [LandMine, AmpField]
        self.tower_dic = {"Tower": Tower,
                          "Mortar Tower": MortarTower,
                          "Rapid-fire Tower": RapidTower,
                          "Landmine": LandMine,
                          "Slow Tower": SlowTower,
                          "Amp Field": AmpField,
                          "Multi Shot Tower": MultiShot}
        self.start_button = pygame.Surface((130, 130))
        self.start_button_rect = pygame.Rect((870, 560), (130, 130))

        self.upgrade_button_rect = None

        self.cursor = pygame.Surface((1000, 700)).convert()
        self.core_health = 100
        self.money = 4000
        self.money_mod = 3
        self.grid = []
        self.start_block = (80, 40)
        self.end_block = None
        self.blocks = pygame.sprite.Group()
        self.hidden_blocks = self.gen_blocks()
        self.path = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.playing = True
        self.can_interact = True
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pos = (self.mouse_x, self.mouse_y)
        self.wave = 0
        self.monsters_dict = {1000: Monster, 500: FastMonster, 125: [ArmorMonster]}

        self.main()

    def main(self):
        self.gen_values()
        self.gen_path()

        for b in self.hidden_blocks:
            if b.is_path and b.pos != self.start_block and b != self.end_block:
                b.image.fill((190, 190, 190))

        # Creating the start button
        self.start_button.fill((0, 255, 0))
        self.start_button.blit(self.font.render("START", 1, (0, 0, 255)), (self.start_button.get_width()/2 -
                                                                           self.font.size("START")[0]/2,
                                                                           self.start_button.get_height()/2 -
                                                                           self.font.get_height()))

        # Adding towers to the shop and displaying them at the bottom
        tower_shop_list = []
        x_val = 10
        y_val = 562
        # Limit 3 towers per row, then wrap back around
        for count, tower in enumerate(self.all_towers):
            if count % 3 == 0 and count != 0:
                y_val += 42
                x_val = 10
            tower_shop_list.append(TowerShopTab(tower((0, 0)), (x_val, y_val)))
            x_val += 133

        # Coloring the borders
        for block in self.hidden_blocks:
            if self.collide_border(block.pos):
                block.is_shown = True
                self.hidden_blocks.remove(block)
                self.blocks.add(block)
                block.color = (25, 25, 25)
                block.image.fill(block.color)

        # Before-loop values
        tower_info = None
        cur_tower = None

        # Main game Loop
        while self.playing:
            # Game Over
            if self.core_health <= 0:
                return

            self.clock.tick(60)
            events = pygame.event.get()
            mouse_button = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            # Main event loop
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                # Mouse motion always checked, even if can_interact is False
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos
                    self.mouse_pos = (self.mouse_x, self.mouse_y)

                # If interaction is off, stop checking events
                if not self.can_interact:
                    break

                # Otherwise, check events
                else:
                    # Left mouse button
                    if mouse_button[0]:
                        # If colliding with a tower in the shop, change the current tower
                        for tower in tower_shop_list:
                            if tower.rect.collidepoint(self.mouse_pos):
                                cur_tower = self.tower_dic[tower.tower.name]
                                break
                        else:
                            # Tower upgrades
                            if self.upgrade_button_rect is not None and self.upgrade_button_rect.collidepoint(self.mouse_pos):
                                if self.money >= tower_info.cost/2:
                                    # .upgrade() returns true or false based on if it can be upgraded again
                                    if tower_info.upgrade():
                                        self.money -= tower_info.cost/2
                            else:
                                # If the play button is pressed, start the wave
                                if self.start_button_rect.collidepoint(self.mouse_pos):
                                    self.monsters = self.gen_monsters(random.randint(10, 25), self.wave)
                                    if len(self.monsters) > 0:
                                        self.start_button.fill((255, 0, 0))
                                        self.start_button.blit(self.font.render("Playing...", 1, (0, 0, 255)),
                                                              (self.start_button.get_width()/2 -
                                                               self.font.size("Playing...")[0]/2,
                                                               self.start_button.get_height()/2 -
                                                               self.font.get_height()))
                                        self.can_interact = False
                                        self.wave += 1
                                    else:
                                        self.start_button.fill((255, 0, 0))
                                        self.start_button.blit(self.font.render("No Path...", 1, (0, 0, 255)),
                                                              (self.start_button.get_width()/2 -
                                                               self.font.size("No Path...")[0]/2,
                                                               self.start_button.get_height()/2 -
                                                               self.font.get_height()))
                                    break
                                else:

                                    # Placing a tower
                                    if cur_tower is not None and not self.collide_border(self.mouse_pos):
                                        if self.money >= cur_tower((0, 0)).cost:

                                            # Ground towers (Landmines, etc)
                                            if cur_tower in self.ground_towers:
                                                for block in [x for x in self.hidden_blocks if x.is_path]:
                                                    if block.rect.collidepoint(self.mouse_pos):
                                                        self.towers.add(cur_tower((block.rect.x, block.rect.y)))
                                                        self.money -= cur_tower((0, 0)).cost
                                                        cur_tower = None
                                                        break
                                                break
                                            else:
                                                # Regular towers
                                                for block in self.blocks:
                                                    if block.rect.collidepoint(self.mouse_pos):
                                                        self.towers.add(cur_tower((block.rect.x, block.rect.y)))
                                                        self.money -= cur_tower((0, 0)).cost
                                                        block.is_shown = True
                                                        cur_tower = None
                                                        break
                                                break
                                    else:
                                        # If clicked on a tower, toggle the info panel
                                        for t in self.towers:
                                            if t.rect.collidepoint(self.mouse_pos):
                                                if tower_info == t:
                                                    tower_info = None
                                                    self.upgrade_button_rect = pygame.Rect((0, 0), (0, 0))
                                                else:
                                                    tower_info = t
                                                    self.upgrade_button_rect = pygame.Rect((t.rect.x + 140,
                                                                                            t.rect.y + 115),
                                                                                           (100, 50))
                                                break
                                        else:
                                            # Create a path
                                            if self.money >= 10:
                                                if not self.collide_border(self.mouse_pos):
                                                    # Makes sure you can't click on the first or end block
                                                    first_last = (self.start_block, self.end_block)
                                                    for block in self.hidden_blocks:
                                                        if block.rect.collidepoint((self.mouse_x, self.mouse_y)):
                                                            if block.pos not in first_last:
                                                                self.money -= 10
                                                                self.hidden_blocks.remove(block)
                                                                self.blocks.add(block)
                                                                block.is_shown = True
                                                                block.is_path = False
                                                                self.update_path()
                                                            break

                    # Middle mouse button (Or the letter T)
                    elif mouse_button[1] or keys[pygame.K_t]:
                        # If you click on a tower, destroy it
                        if not self.collide_border(self.mouse_pos):
                            for tower in self.towers:
                                if tower.rect.collidepoint((self.mouse_x, self.mouse_y)):
                                    self.money += tower.value/2
                                    tower.kill()
                                    cur_tower = tower_info = None
                                    break

                    # Right mouse button (Or the letter U)
                    elif mouse_button[2] or keys[pygame.K_u]:
                        cur_tower = None
                        # If a block is clicked, remove it
                        if not self.collide_border(self.mouse_pos):
                            tower_info = None
                            for block in self.blocks:
                                if block.rect.collidepoint(self.mouse_pos):
                                    self.money += 10
                                    self.blocks.remove(block)
                                    self.hidden_blocks.add(block)
                                    block.is_shown = False
                                    self.update_path()
                                    break

            # Wave is over if all monsters are dead
            if len(self.monsters) == 0 and not self.can_interact:
                self.can_interact = True
                self.start_button.fill((0, 255, 0))
                self.start_button.blit(self.font.render("START", 1, (0, 0, 255)), (self.start_button.get_width()/2 -
                                                                                   self.font.size("START")[0]/2,
                                                                                   self.start_button.get_height()/2 -
                                                                                   self.font.get_height()))
                # Adds the money for the turn
                for tower in self.towers:
                    self.money += tower.turn_yield*self.money_mod
                    tower.turn_yield = 0

            # Clear the screen to prepare for re-blit
            self.game_window.fill((255, 255, 255))
            self.game_surface.fill((255, 255, 255))
            self.bottom_bar.fill((40, 60, 140))

            # Game_Surface blitting #

            # Blits the hidden blocks
            for hidden in self.hidden_blocks:
                if hidden.is_path:
                    self.game_surface.blit(hidden.image, hidden.pos)

            self.path.draw(self.game_surface)
            self.blocks.draw(self.game_surface)

            # Subtracts HP from the core if the monster gets through
            for monster in self.monsters:
                self.core_health -= monster.update(self.game_surface)

            # Draws to the screen
            self.monsters.draw(self.game_surface)
            self.towers.update(self.monsters, self.game_surface, self.game_surface_rect)
            self.towers.draw(self.game_surface)
            self.game_window.blit(self.game_surface, (0, 0))

            # Bottom_Bar blitting #
            self.bottom_bar.blit(self.start_button, (self.bottom_bar.get_width() - self.start_button.get_width(), 0))
            hp_text = "Health: "+str(self.core_health)
            money_text = "Money: $"+str(self.money)
            self.bottom_bar.blit(self.font.render(hp_text, 1, (255, 0, 0)), (self.bottom_bar.get_width() -
                                                                             self.start_button.get_width() -
                                                                             self.info_box.surface.get_width() -
                                                                             self.font.size(hp_text)[0]-20, 20))

            self.bottom_bar.blit(self.font.render(money_text, 1, (0, 255, 0)), (self.bottom_bar.get_width() -
                                                                                self.start_button.get_width() -
                                                                                self.info_box.surface.get_width() -
                                                                                self.font.size(hp_text)[0]-20, 70))

            # Blits the picture of the tower to the bottom bar
            for tower in tower_shop_list:
                self.bottom_bar.blit(tower.surface, (tower.rect.x, tower.rect.y - 560))

            # Info box blitting
            for obj in list(self.monsters) + list(self.towers) + tower_shop_list:
                if obj.rect.collidepoint(self.mouse_pos):
                    hover_obj = obj
                    break
            else:
                hover_obj = None

            self.info_box.update(hover_obj)
            self.bottom_bar.blit(self.info_box.surface, (self.bottom_bar.get_width() -
                                                         self.start_button.get_width() -
                                                         self.info_box.surface.get_width(), 0))

            self.bottom_bar_outline.blit(self.bottom_bar, (5, 5))
            self.game_window.blit(self.bottom_bar_outline, (0, 560))

            # Visualized tower radius when placing
            if cur_tower is not None or tower_info is not None:
                self.cursor.fill((127, 33, 33))
                self.cursor.set_colorkey((127, 33, 33))
                if cur_tower is not None:
                    the_t = cur_tower((0, 0))
                    pygame.draw.circle(self.cursor, (255, 0, 0), self.mouse_pos, the_t.radius)
                    self.cursor.blit(the_t.image, (self.mouse_x - the_t.image.get_width()/2,
                                                   self.mouse_y - the_t.image.get_height()/2))
                else:
                    the_t = tower_info
                    pygame.draw.circle(self.cursor, (255, 0, 0), the_t.rect.center, the_t.radius)
                    self.game_window.blit(tower_info.frame.image, (tower_info.rect.x +
                                                                   tower_info.image.get_width(),
                                                                   tower_info.rect.y -
                                                                   tower_info.frame.image.get_height()/2))
                self.cursor.set_alpha(75)
                self.game_window.blit(self.cursor, (0, 0))

            pygame.display.flip()

    # Returns true if the point is in the map_border, false if not
    def collide_border(self, point):
        for border in self.border_list:
            if border.collidepoint(point):
                return True
        return False

    # Creates all of the blocks on the screen.
    def gen_blocks(self):
        ret_group = pygame.sprite.Group()
        y_value = 0
        for y in range(14):
            x_value = 0
            row = []
            for x in range(25):

                # Ending block
                if (x_value, y_value) != (840, 480):
                    # Starting block
                    if (x_value, y_value) == (80, 40):
                        b = Block((x_value, y_value), False)
                        b.color = (0, 0, 255)
                        b.image.fill((0, 0, 255))
                    else:
                        b = Block((x_value, y_value), False)
                else:
                    b = Block((x_value, y_value), True)
                    b.color = (255, 0, 0)
                    b.image.fill((255, 0, 0))
                    self.end_block = b

                ret_group.add(b)
                row.append(b)
                x_value += 40
            self.grid.append(row)
            y_value += 40

        for b in ret_group:
            b.get_neighbors(self.grid)
        return ret_group

    # Generates the pathing values for all blocks on the screen
    def gen_values(self):
        for reset in self.hidden_blocks:
            reset.path_value = 0
            reset.is_path = False

        for reset in self.blocks:
            reset.path_value = 0
            reset.is_path = False

        blocks = [self.end_block]
        checked = [self.end_block]
        while len(blocks) > 0:
            look_at = blocks.pop(0)
            for block in look_at.neighbors:
                if block not in checked:
                    if block.is_shown is False:
                        the_val = look_at.path_value + 1
                        block.path_value = the_val
                        checked.append(block)
                        blocks.append(block)

    # Generates the shortest path through the blocks and gives it to the monsters
    def gen_path(self):
        ret_path = []
        checked = set()
        self.path = pygame.sprite.Group()
        for b in self.hidden_blocks:
            if b.pos == (80, 40):
                b.is_path = True
                ret_path.append(b)
                checked.add(b)
                break

        finding_path = True
        while finding_path:
            cur_neighbors = ret_path[-1].neighbors
            if all(neighbor in checked for neighbor in cur_neighbors):
                finding_path = False
            for neighbor in cur_neighbors:
                if not neighbor.is_shown:
                    if neighbor.path_value < ret_path[-1].path_value and neighbor not in checked:
                        ret_path.append(neighbor)
                        neighbor.is_path = True
                        if neighbor != self.end_block:
                            neighbor.image.fill((190, 190, 190))

                        if neighbor.path_value == 0:
                            finding_path = False
                        break
                if neighbor not in checked:
                    checked.add(neighbor)

        self.path.add(ret_path)
        if len(ret_path) <= 1:
            self.start_button.fill((255, 0, 0))
            self.start_button.blit(self.font.render("No Path...", 1, (0, 0, 255)),
                                  (self.start_button.get_width()/2 -
                                   self.font.size("No Path...")[0]/2,
                                   self.start_button.get_height()/2 -
                                   self.font.get_height()))
        else:
            self.start_button.fill((0, 255, 0))
            self.start_button.blit(self.font.render("START", 1, (0, 0, 255)), (self.start_button.get_width()/2 -
                                                                               self.font.size("START")[0]/2,
                                                                               self.start_button.get_height()/2 -
                                                                               self.font.get_height()))
        return ret_path

    # Generates the wave of monsters
    def gen_monsters(self, number, wave):
        ret_group = pygame.sprite.Group()

        self.gen_values()

        path = self.gen_path()

        # Gen_path will return a list with a length of 1 if there is no valid path
        # So we don't spawn monsters if the path isn't valid
        if len(path) > 1:
            # Randomly selects which monsters to spawn
            for x in range(number):
              r = random.randint(0, 1000)
              selected = None
              # Loops through the monster dictionary and randomly decides what to choose
              for key, monster in iter(sorted(self.monsters_dict.iteritems())):
                if r < key:
                  if type(monster) is list:
                    selected = random.choice(monster)
                    break
                  else:
                    selected = monster
                    break
              else:
                selected = Monster
              ret_group.add(selected(random.randint(1, 5), list(path)))

        return ret_group

    def update_path(self):
        self.gen_values()
        self.gen_path()
        for a in self.blocks:
            if not a.is_path:
                a.image.fill(a.color)


if __name__ == "__main__":
    Game()
