from pygame import Surface

# TODO: make this inherit from pygame.Surface and be a Surface object
class OutlinedSurface():
    def __init__(self, surface, offset, bgcolor=(255, 255, 255)):
        self.inside_surface = surface
        self.offset = offset
        self.bgcolor = bgcolor

        self.surface = Surface((self.inside_surface.get_width() + offset*2,
                                self.inside_surface.get_height() + offset*2)).convert()
        self.surface.fill(self.bgcolor)
        self.surface.blit(self.inside_surface, (offset, offset))
