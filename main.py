# Pygame Tower Defense
# Brandon Sturgeon

import pygame
import random
import time
import math

from lib.block import Block

from lib.monster import Monster
from lib.fast_monster import FastMonster
from lib.armor_monster import ArmorMonster

from lib.tower import Tower
from lib.mortar_tower import MortarTower
from lib.rapid_tower import RapidTower
from lib.landmine import LandMine
from lib.slow_tower import SlowTower
from lib.amp_field import AmpField
from lib.multi_shot_tower import MultiShot

from lib.tower_shop_tab import TowerShopTab
from lib.info_tab import InfoTab

# Main game class
class Game():
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        flags = pygame.DOUBLEBUF | pygame.FULLSCREEN | pygame.HWSURFACE
        self.game_window = pygame.display.set_mode((1000, 700), flags)
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
        self.start_button = pygame.Surface((130, 130)).convert()
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

        # Used to randomly seelct a group of monsters.
        # Structure is Number: ClassName (Or List with Classnames)
        # The lower the number, the lower the chance of spawning.
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

        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEMOTION])
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
                if keys[pygame.K_q]:
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
            self.towers.update(self.monsters, self.game_surface, self.game_surface_rect)
            self.towers.draw(self.game_surface)
            self.monsters.draw(self.game_surface)
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
            # Randomly generates a number between 1 and 1000, and then goes through the monsters_dictionary
            # In ascending order and checks if the number is less than the monster's generation value
            # Then chooses a monster to spawn
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
