from pygame import Surface, Rect, font, transform

# A tab for each tower down at the bottom
class TowerShopTab():
    def __init__(self, tower, pos):
        self.pos = pos
        self.tower = tower
        self.name = self.tower.name
        self.description = self.tower.description
        self.surface_inside = Surface((123, 38)).convert()
        self.surface_inside.fill((100, 100, 100))
        self.image = tower.image
        self.cost = tower.cost
        self.surface = Surface((125, 40)).convert()
        self.rect = Rect(self.pos, self.surface .get_size())
        self.font = font.Font(None, 15)
        self.info_tab = tower.frame.image

        self.surface_inside.blit(transform.scale(self.tower.image, (20, 20)), (5, 10))
        self.surface_inside.blit(self.font.render(self.tower.name, 1, (0, 0, 0)), (30, 25-self.font.get_height()))
        self.surface .blit(self.surface_inside, (1, 1))

    def get_surface(self):
        return self.surface


