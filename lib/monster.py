from pygame import sprite, Surface, Rect
import time

# Base Monster class
class Monster(sprite.Sprite):
    def __init__(self, move_time, nodes):
        sprite.Sprite.__init__(self)
        self.nodes = nodes
        self.orig_nodes = nodes
        self.move_time = move_time
        self.spawn_time = time.time()
        self.image = Surface((40, 40)).convert()
        self.image_inside = Surface((38, 38)).convert()
        self.image_inside.fill((0, 255, 0))
        self.image.blit(self.image_inside, (1, 1))
        self.pos = (80, 40)
        self.real_pos = (80, 40)
        self.rect = Rect(self.pos, self.image.get_size())
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
