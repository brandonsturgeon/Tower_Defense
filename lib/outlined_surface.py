from pygame import Surface

class OutlinedSurface():
    def __init__(self, surface, offset, bgcolor=(255, 255, 255)):
        self.inside_surface = surface
        self.offset = offset
        self.bgcolor = bgcolor

        self.surface = pygame.Surface((self.inside_surface.get_width() + offset*2,
                                       self.inside_surface.get_height() + offset*2)).convert()
        self.surface.fill(self.bgcolor)
        self.surface.blit(self.inside_surface, (offset, offset))
