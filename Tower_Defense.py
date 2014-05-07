# Pygame Tower Defense
# Brandon Sturgeon


import pygame
import random
import time

class OutlinedSurface():
    def __init__(self, surface, offset, bgcolor=(0, 0, 0)):
        self.inside_surface = surface
        self.offset = offset
        self.bgcolor = bgcolor

        self.surface = pygame.Surface((self.inside_surface.get_width() + offset*2,
                                       self.inside_surface.get_height() + offset*2))
        self.surface.fill(self.bgcolor)
        self.surface.blit(self.inside_surface, (offset, offset))


class Block(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.image = pygame.Surface((40, 40))
        self.image.fill((175, 175, 175))
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        self.is_shown = True


# Base Monster class
class Monster(pygame.sprite.Sprite):
    def __init__(self, move_time):
        pygame.sprite.Sprite.__init__(self)
        self.move_time = move_time
        self.spawn_time = time.time()
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 255, 0))
        self.pos = (40, 0)
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        self.direction = "DOWN"
        self.speed = 1
        self.dir_dic = {"UP": (0, -self.speed), "DOWN": (0, self.speed),
                        "LEFT": (-self.speed, 0), "RIGHT": (self.speed, 0)}
        self.dir_opps = {"UP": "DOWN",
                         "LEFT": "RIGHT"}
        self.value = 1
        self.health = 100

    def update(self, blocks, window):
        if time.time() - self.spawn_time >= self.move_time:
            blocks = [x.rect for x in blocks]

            temp_rect = self.rect.copy()
            if temp_rect.move(self.dir_dic[self.direction]).collidelist(blocks) != -1:
                self.find_new_dir(blocks)
            self.rect.move_ip(self.dir_dic[self.direction])

            if self.rect.top >= window.get_height():
                self.kill()
                return self.value

            if self.rect.left >= window.get_width():
                self.kill()
                return self.value

            if self.rect.bottom <= 0:
                self.kill()
                return self.value

            if self.health <= 0:
                self.kill()
        return 0

    def find_new_dir(self, blocks):
        possible_dirs = [x for x in self.dir_dic.keys() if x != self.direction]
        for k, v in self.dir_opps.items():
            if k == self.direction:
                possible_dirs.remove(v)
            if v == self.direction:
                possible_dirs.remove(k)

        for poss in possible_dirs:
            if self.rect.move(self.dir_dic[poss]).collidelist(blocks) != -1:
                possible_dirs.remove(poss)

        self.direction = random.choice(possible_dirs)


class FastMonster(Monster):
    def __init__(self, move_time):
        Monster.__init__(self, move_time)
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 0))
        self.rect = pygame.Rect(self.pos, (40, 40))
        self.speed = 2
        self.value = 0.5


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, target, image, speed, damage):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.target = target
        self.image = image
        self.speed = speed
        self.damage = damage
        self.rect = pygame.Rect(self.pos, self.image.get_size())

        self.x_speed = -int((self.rect.centerx - self.target.rect.centerx)/self.speed)
        self.y_speed = -int((self.rect.centery - self.target.rect.centery)/self.speed)

    def update(self, monsters, screen):
        if self.target is None:
            self.kill()
            return

        #self.x_speed = -int((self.rect.centerx - self.target.rect.centerx)/self.speed)
        #self.y_speed = -int((self.rect.centery - self.target.rect.centery)/self.speed)

        width_calc = self.target.image.get_width()/2 + self.image.get_width()
        height_calc = self.target.image.get_height()/2 + self.image.get_height()

        # If the bullet is within range, it hit the target
        if abs(self.rect.centerx - self.target.rect.centerx) <= width_calc:
            if abs(self.rect.centery - self.target.rect.centery) <= height_calc:
                self.target.health -= self.damage
                self.kill()
            else:
                self.rect.move_ip((self.x_speed, self.y_speed))
        else:
            self.rect.move_ip((self.x_speed, self.y_speed))

        if not screen.contains(self.rect):
            self.kill()


class MortarShell(Projectile):
    def __init__(self, pos, target, image, speed, damage):
        Projectile.__init__(self, pos, target, image, speed, damage)
        self.radius = 50

    def update(self, monsters, screen):
        if self.target is None:
            self.kill()
            return

        #self.x_speed = -int((self.rect.centerx - self.target.rect.centerx)/self.speed)
        #self.y_speed = -int((self.rect.centery - self.target.rect.centery)/self.speed)

        width_calc = self.target.image.get_width()/2 + self.image.get_width()
        height_calc = self.target.image.get_height()/2 + self.image.get_height()

        # If the bullet is within range, it hit the target
        if abs(self.rect.centerx - self.target.rect.centerx) <= width_calc:
            if abs(self.rect.centery - self.target.rect.centery) <= height_calc:

                # Splash damage
                for monster in monsters:
                    if pygame.sprite.collidecircle(self, monster):
                        self.target.health -= self.damage
                        self.kill()
            else:
                self.rect.move_ip((self.x_speed, self.y_speed))
        else:
            self.rect.move_ip((self.x_speed, self.y_speed))

        if not screen.contains(self.rect):
            self.kill()


class TowerFrame():
    def __init__(self, tower):
        self.tower = tower
        self.image = pygame.Surface((200, 300))
        self.image.fill((175, 175, 175))
        self.s_width = self.image.get_width()
        self.s_height = self.image.get_height()

        self.t_attributes = {"Name": self.tower.name,
                             "Fire Rate": self.tower.fire_rate,
                             "Damage": self.tower.damage,
                             "DPS": self.tower.damage/self.tower.fire_rate}
        self.font = pygame.font.Font(None, 18)

        self.image.blit(self.tower.image, (self.s_width/2 - self.tower.image.get_width()/2, 2))

        y_value = self.tower.image.get_width() + 7

        # Blits the tower description
        for desc in self.length_splitter(self.font, self.tower.description, self.image.get_width() - 5):
            self.image.blit(self.font.render(desc, 1, (0, 0, 0)), (5, y_value))
            y_value += self.font.get_height() + 1
        y_value += 5

        # Blits the tower's attributes
        for attr in ["Name", "Fire Rate", "Damage", "DPS"]:
            value = self.t_attributes[attr]
            self.image.blit(self.font.render(attr + ": " + str(value), 1, (0, 0, 0)), (5, y_value))
            y_value += self.font.get_height() + 1

        self.image = OutlinedSurface(self.image, 5).surface

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
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 0, 0))
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        self.projectile = pygame.Surface((10, 10))
        self.projectile.fill((0, 255, 255))
        self.projectile_speed = 20
        self.projectiles = pygame.sprite.Group()

        self.radius = 200
        self.fire_rate = 1
        self.damage = 25
        self.level = 1
        self.description = "A basic tower with moderate fire speed and damage."

        self.target = None
        self.last_shot = time.time()

        self.frame = TowerFrame(self)

    def update(self, monsters, screen, screen_rect):

        # If there is no target
        if self.target is None:
            for monster in monsters:
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

    def shoot(self):
        if time.time() - self.last_shot >= self.fire_rate:
            self.projectiles.add(Projectile(pos=(self.rect.x, self.rect.y),
                                            target=self.target,
                                            image=self.projectile,
                                            speed=self.projectile_speed,
                                            damage=self.damage))
            self.last_shot = time.time()


class MortarTower(Tower):
    def __init__(self, pos):
        Tower.__init__(self, pos)
        self.name = "Mortar Tower"
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 0, 255))
        self.projectile = pygame.Surface((15, 15))
        self.projectile.fill((255, 150, 0))
        self.projectile_speed = 30

        self.radius = 400
        self.fire_rate = 3
        self.damage = 15
        self.description = "A long-range tower that fires mortars which " \
                           "explode on impact, dealing damage to all nearby enemies."

    def shoot(self):
        if time.time() - self.last_shot >= self.fire_rate:
            self.projectiles.add(MortarShell(pos=(self.rect.x, self.rect.y),
                                             target=self.target,
                                             image=self.projectile,
                                             speed=self.projectile_speed,
                                             damage=self.damage))
            self.last_shot = time.time()


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


class Game():
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.game_window = pygame.display.set_mode((1000, 700))
        self.game_window.fill((0, 255, 255))
        self.game_surface = pygame.Surface((1000, 560))
        self.game_surface_rect = pygame.Rect((0, 0), self.game_surface.get_size())
        self.bottom_bar = pygame.Surface((1000, 140))
        self.bottom_bar.fill((190, 115, 0))
        self.bottom_bar_rect = pygame.Rect((0, 560), self.bottom_bar.get_size())
        self.core_health = 100
        self.blocks = self.gen_blocks()
        self.hidden_blocks = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.playing = True
        self.can_interact = True
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pos = (self.mouse_x, self.mouse_y)
        self.wave = 0
        self.main()

    def main(self):

        cur_tower = None
        # Main game Loop
        while self.playing:
            self.clock.tick(60)
            events = pygame.event.get()
            mouse_button = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                # Only in between waves
                if self.can_interact:
                    if event.type == pygame.MOUSEMOTION:
                        self.mouse_x, self.mouse_y = event.pos
                        self.mouse_pos = (self.mouse_x, self.mouse_y)

                    # Left mouse button removes blocks
                    if mouse_button[0] == 1:
                        for tower in self.towers:
                            if tower.rect.collidepoint(self.mouse_pos):
                                if cur_tower == tower:
                                    cur_tower = None
                                else:
                                    cur_tower = tower
                                break
                        else:
                            cur_tower = None
                            for block in self.blocks:
                                if block.rect.collidepoint((self.mouse_x, self.mouse_y)):
                                    self.blocks.remove(block)
                                    self.hidden_blocks.add(block)

                    # Middle mouse button toggles towers
                    elif keys[pygame.K_t] == 1:
                        for tower in self.towers:
                            if tower.rect.collidepoint((self.mouse_x, self.mouse_y)):
                                tower.kill()
                                break
                        else:
                            for block in self.blocks:
                                if block.rect.collidepoint((self.mouse_x, self.mouse_y)):
                                    self.towers.add(Tower((block.rect.x, block.rect.y)))

                    # Right mouse button places blocks
                    elif mouse_button[2] == 1:
                        for block in self.hidden_blocks:
                            if block.rect.collidepoint((self.mouse_x, self.mouse_y)):
                                self.hidden_blocks.remove(block)
                                self.blocks.add(block)

                    # Q starts the wave
                    if keys[pygame.K_q]:
                        self.can_interact = False
                        self.wave += 1
                        self.monsters = self.gen_monsters(random.randint(10, 25), self.wave)
                        break

            # Wave is over if all monsters are dead
            if len(self.monsters) == 0:
                self.can_interact = True
            
            self.game_window.fill((255, 255, 255))
            self.game_surface.fill((255, 255, 255))
            self.blocks.draw(self.game_surface)
            for monster in self.monsters:
                self.core_health -= monster.update(self.blocks, self.game_surface)
            self.monsters.draw(self.game_surface)
            self.towers.update(self.monsters, self.game_surface, self.game_surface_rect)
            self.towers.draw(self.game_surface)

            self.game_window.blit(self.game_surface, (0, 0))
            self.game_window.blit(self.bottom_bar, (0, 560))
            if cur_tower is not None:
                self.game_window.blit(cur_tower.frame.image, (cur_tower.rect.x + cur_tower.image.get_width(),
                                                              cur_tower.rect.y - cur_tower.frame.image.get_height()/2))
            pygame.display.flip()

    @staticmethod
    def gen_blocks():
        ret_group = pygame.sprite.Group()

        y_value = 0
        for y in range(14):
            x_value = 0
            for x in range(32):
                ret_group.add(Block((x_value, y_value)))
                x_value += 40
            y_value += 40
        return ret_group

    @staticmethod
    def gen_monsters(number, wave):
        ret_group = pygame.sprite.Group()

        for x in range(number):
            ret_group.add(Monster(x))

        return ret_group

if __name__ == "__main__":
    Game()
