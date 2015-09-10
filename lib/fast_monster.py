from pygame import Surface, Rect
from monster import Monster

class FastMonster(Monster):
    def __init__(self, move_time, nodes):
        Monster.__init__(self, move_time, nodes)
        self.image = Surface((20, 20)).convert()
        self.image_inside = Surface((18, 18)).convert()
        self.image_inside.fill((255, 255, 0))
        self.image.blit(self.image_inside, (1, 1))
        self.rect = Rect(self.pos, (40, 40))
        self.speed = 4
        self.diag_speed = 3
        self.value = 0.5
        self.health = 50
        self.name = "Fast Monster"
        self.description = "A small monster with very quick movement speed, but low health."

