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
        self.image.fill(self.color)
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        self.is_shown = False
        self.neighbors = set()
        self.path_value = 0
        self.is_end = is_end

    def get_neighbors(self, lst):
        for b in lst:
            if self in b:
                a = self
                if b.index(a) != 0:
                    to_add = b[b.index(a)-1]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(b[b.index(a)-1])

                if b.index(a) != len(b)-1:
                    to_add = b[b.index(a)+1]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(b[b.index(a)+1])

                if lst.index(b) != 0:
                    to_add = lst[lst.index(b)-1][b.index(a)]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(lst[lst.index(b)-1][b.index(a)])

                if lst.index(b) != len(lst)-1:
                    to_add = lst[lst.index(b)+1][b.index(a)]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(lst[lst.index(b)+1][b.index(a)])


# Base Monster class
class Monster(pygame.sprite.Sprite):
    def __init__(self, move_time):
        pygame.sprite.Sprite.__init__(self)
        self.nodes = None
        self.move_time = move_time
        self.spawn_time = time.time()
        self.image = pygame.Surface((40, 40)).convert()
        self.image_inside = pygame.Surface((38, 38)).convert()
        self.image_inside.fill((0, 255, 0))
        self.image.blit(self.image_inside, (1, 1))
        self.pos = (80, 40)
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        self.speed = 1
        self.diag_speed = 2
        self.target_pos = (880, 560)
        self.value = 1
        self.health = 100

    def update(self, blocks, window):
        if time.time() - self.spawn_time >= self.move_time:
            blocks = [x.rect for x in blocks]
            need_move = True

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

    # Finds a new direction for the monster to go if they hit a wall
    def find_new_dir(self, blocks):
        pass


class FastMonster(Monster):
    def __init__(self, move_time):
        Monster.__init__(self, move_time)
        self.image = pygame.Surface((20, 20)).convert()
        self.image_inside = pygame.Surface((18, 18)).convert()
        self.image_inside.fill((255, 255, 0))
        self.image.blit(self.image_inside, (1, 1))
        self.rect = pygame.Rect(self.pos, (40, 40))
        self.speed = 2
        self.diag_speed = 3
        self.value = 0.5
        self.health = 50


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, target, image, speed, damage):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
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
        if self.target is None:
            self.kill()
            return

        # Calculates where the projectile needs to go
        self.angle = math.atan2((self.target.rect.centery-self.rect.centery),
                                (self.target.rect.centerx-self.rect.centerx))
        self.x_speed = math.cos(self.angle)*self.speed
        self.y_speed = math.sin(self.angle)*self.speed

        # If the bullet is within range, it hit the target
        if abs(self.rect.centerx - self.target.rect.centerx) <= 10:
            if abs(self.rect.centery - self.target.rect.centery) <= 10:
                self.do_damage(monsters)
                self.kill()
            else:
                self.rect.move_ip((self.x_speed, self.y_speed))
        else:
            self.rect.move_ip((self.x_speed, self.y_speed))

        if not screen.contains(self.rect):
            self.kill()

    def do_damage(self, monsters):
        for monster in monsters:
            if monster == self.target:
                monster.health -= self.damage
                break


class MortarShell(Projectile):
    def __init__(self, pos, target, image, speed, damage):
        Projectile.__init__(self, pos, target, image, speed, damage)
        self.radius = 50

    def do_damage(self, monsters):
        for monster in monsters:
            if pygame.sprite.collide_circle(self, monster):
                monster.health -= self.damage


class TowerFrame():
    def __init__(self, tower):
        self.tower = tower
        self.image = pygame.Surface((200, 300)).convert()
        self.image.fill((200, 115, 0))
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
        self.grid_pos = tuple([x/40 for x in self.pos])
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 0, 0))
        self.rect = pygame.Rect(self.pos, self.image.get_size())
        self.projectile = pygame.Surface((10, 10))
        self.projectile.fill((0, 255, 255))
        self.projectile_speed = 5
        self.projectiles = pygame.sprite.Group()

        self.radius = 200
        self.fire_rate = 1
        self.damage = 25
        self.level = 1
        self.description = "A basic tower with moderate fire speed and damage."
        self.cost = 25

        self.target = None
        self.last_shot = time.time()

        self.image.convert()
        self.projectile.convert()
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
        self.projectile_speed = 3

        self.radius = 400
        self.fire_rate = 3
        self.damage = 15
        self.description = "A long-range tower that fires mortars which " \
                           "explode on impact, dealing damage to all nearby enemies."
        self.cost = 75

        self.frame = TowerFrame(self)

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
        self.description = "A tower with moderate range and very quick attack speed."
        self.cost = 50

        self.frame = TowerFrame(self)


class TowerShopTab():
    def __init__(self, tower, pos):
        self.pos = pos
        self.tower = tower
        self.surface_inside = pygame.Surface((123, 38)).convert()
        self.surface_inside.fill((100, 100, 100))
        self.surface = pygame.Surface((125, 40)).convert()
        self.rect = pygame.Rect(self.pos, self.surface.get_size())
        self.font = pygame.font.Font(None, 15)
        self.info_tab = tower.frame.image

        self.surface_inside.blit(pygame.transform.scale(self.tower.image, (20, 20)), (5, 10))
        self.surface_inside.blit(self.font.render(self.tower.name, 1, (0, 0, 0)), (30, 25-self.font.get_height()))
        self.surface.blit(self.surface_inside, (1, 1))

    def get_surface(self):
        return self.surface


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

        self.all_towers = [Tower, MortarTower, RapidTower]
        self.tower_dic = {"Tower": Tower, "Mortar Tower": MortarTower, "Rapid-fire Tower": RapidTower}
        self.core_health = 100
        self.money = 200
        self.grid = []
        self.end_block = None
        self.blocks = pygame.sprite.Group()
        self.hidden_blocks = self.gen_blocks()
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
        # Creating the start button
        start_button = pygame.Surface((130, 130))
        start_button_rect = pygame.Rect((870, 560), (130, 130))
        start_button.fill((0, 255, 0))
        start_button.blit(self.font.render("START", 1, (0, 0, 255)), (start_button.get_width()/2 -
                                                                      self.font.size("PLAY")[0]/2,
                                                                      start_button.get_height()/2 -
                                                                      self.font.get_height()))

        # Adding towers to the shop
        tower_shop_list = []
        x_val = 10
        for tower in self.all_towers:
            tower_shop_list.append(TowerShopTab(tower((0, 0)), (x_val, 50 + 560)))
            x_val += 133

        # Coloring the borders
        for block in self.hidden_blocks:
            if self.collide_border(block.pos):
                block.is_shown = True
                self.hidden_blocks.remove(block)
                self.blocks.add(block)
                block.image.fill((25, 25, 25))

        # Before-loop values
        tower_info = None
        cur_tower = Tower

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

                    # Left mouse button
                    if mouse_button[0] == 1:
                        # Collide with tower in the shop?
                        for tower in tower_shop_list:
                            if tower.rect.collidepoint(self.mouse_pos):
                                cur_tower = self.tower_dic[tower.tower.name]
                                print "Changing Tower to: " + str(cur_tower)
                                break
                        else:
                            # Collide with play_button?
                            if start_button_rect.collidepoint(self.mouse_pos):
                                self.can_interact = False
                                self.wave += 1
                                self.monsters = self.gen_monsters(random.randint(10, 25), self.wave)
                                break
                            else:
                                # Collide with a tower?
                                for t in self.towers:
                                    if t.rect.collidepoint(self.mouse_pos):
                                        if tower_info == t:
                                            tower_info = None
                                        else:
                                            tower_info = t
                                        break
                                else:
                                    # Collide with a block?
                                    if not self.collide_border(self.mouse_pos):
                                        tower_info = None
                                        for block in self.blocks:
                                            if block.rect.collidepoint(self.mouse_pos):
                                                self.blocks.remove(block)
                                                self.hidden_blocks.add(block)
                                                self.grid[block.grid_pos[0]][block.grid_pos[1]] = True

                    # Middle mouse button
                    elif mouse_button[1] == 1 or keys[pygame.K_t]:
                        if not self.collide_border(self.mouse_pos):
                            for tower in self.towers:
                                if tower.rect.collidepoint((self.mouse_x, self.mouse_y)):
                                    self.grid[tower.grid_pos[0]][tower.grid_pos[1]] = True
                                    tower.kill()
                                    break
                            else:
                                for block in self.blocks:
                                    if block.rect.collidepoint((self.mouse_x, self.mouse_y)):
                                        self.towers.add(cur_tower((block.rect.x, block.rect.y)))
                                        self.grid[block.grid_pos[0]][block.grid_pos[1]] = False

                    # Right mouse button
                    elif mouse_button[2] == 1:
                        if not self.collide_border(self.mouse_pos):
                            for block in self.hidden_blocks:
                                if block.rect.collidepoint((self.mouse_x, self.mouse_y)):
                                    self.hidden_blocks.remove(block)
                                    self.blocks.add(block)
                                    self.grid[block.grid_pos[0]][block.grid_pos[1]] = False

            # Wave is over if all monsters are dead
            if len(self.monsters) == 0:
                self.can_interact = True
            
            self.game_window.fill((255, 255, 255))
            self.game_surface.fill((255, 255, 255))
            self.bottom_bar.fill((40, 60, 140))

            # Game_Surface blitting
            self.blocks.draw(self.game_surface)
            self.hidden_blocks.draw(self.game_surface)
            for monster in self.monsters:
                self.core_health -= monster.update(self.blocks, self.game_surface)
            self.monsters.draw(self.game_surface)
            self.towers.update(self.monsters, self.game_surface, self.game_surface_rect)
            self.towers.draw(self.game_surface)
            self.game_window.blit(self.game_surface, (0, 0))

            # Bottom_Bar blitting
            self.bottom_bar.blit(start_button, (self.bottom_bar.get_width() - start_button.get_width(), 0))
            for tower in tower_shop_list:
                self.bottom_bar.blit(tower.surface, (tower.rect.x, tower.rect.y - 560))

            self.bottom_bar_outline.blit(self.bottom_bar, (5, 5))
            self.game_window.blit(self.bottom_bar_outline, (0, 560))

            # High-level blitting
            if tower_info is not None:
                self.game_window.blit(tower_info.frame.image, (tower_info.rect.x +
                                                               tower_info.image.get_width(),
                                                               tower_info.rect.y -
                                                               tower_info.frame.image.get_height()/2))
            pygame.display.flip()

    # True if the point is in the map_border, false if not
    def collide_border(self, point):
        for border in self.border_list:
            if border.collidepoint(point):
                return True
        return False

    def gen_blocks(self):
        ret_group = pygame.sprite.Group()
        y_value = 0
        for y in range(14):
            x_value = 0
            row = []
            for x in range(25):
                if (x_value, y_value) != (840, 480):
                    b = Block((x_value, y_value), False)
                else:
                    b = Block((x_value, y_value), True)
                    self.end_block = b
                ret_group.add(b)
                row.append(b)
                x_value += 40
            self.grid.append(row)
            y_value += 40

        for b in ret_group:
            b.get_neighbors(self.grid)
        return ret_group

    def gen_path(self):
        is_pathing = True
        the_blocks = [self.end_block]
        checked = [self.end_block]
        the_val = 1
        font = pygame.font.Font(None, 30)
        while is_pathing:
            if len(checked) >= len(self.hidden_blocks):
                break

            for block in the_blocks:
                for neighbor in block.neighbors:
                    if neighbor not in checked and neighbor not in the_blocks:
                        if neighbor.is_shown is False:
                            neighbor.path_value = the_val
                            neighbor.image = OutlinedSurface(pygame.transform.scale(font.render(str(neighbor.path_value), 1, (0, 0, 0)), (38, 38)), 1).surface
                            checked.append(neighbor)
                            the_blocks.append(neighbor)
                the_val += 1

            self.game_window.fill((0, 0, 0))
            self.game_surface.fill((255, 255, 255))
            self.blocks.draw(self.game_surface)
            self.hidden_blocks.draw(self.game_surface)
            self.game_window.blit(self.game_surface, (0, 0))
            pygame.display.flip()
        print "Out"

    def gen_monsters(self, number, wave):
        ret_group = pygame.sprite.Group()

        self.gen_path()
        # Randomly selects monsters to spawn
        for x in range(number):
            add_monster = random.choice([Monster, FastMonster])
            ret_group.add(add_monster(random.randint(1, 5)))

        return ret_group


if __name__ == "__main__":
    Game()
