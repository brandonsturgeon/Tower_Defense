from pygame import Rect
from monster import Monster

class ArmorMonster(Monster):
  def __init__(self, move_time, nodes):
    Monster.__init__(self, move_time, nodes)
    self.image_inside.fill((142, 163, 12))
    self.image.blit(self.image_inside, (1, 1))
    self.rect = Rect(self.pos, (40, 40))
    self.speed = 1
    self.diag_speed = 3
    self.value = 10
    self.health = 100
    self.armor = 500

    self.name = "Armored Monster"
    self.description = "An armored monster that takes progressively more damage as it is hit"

    # Does damage to the monster and checks if it dies TODO: This armor system is just an armor system right now
    # Need to keep track of how many times it's been hit and multiply damage by some amount modified by how many times it's been hit
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

