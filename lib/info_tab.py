from pygame import Surface, font, transform

class InfoTab():
    def __init__(self):
        self.surface_inside = Surface((295, 128)).convert()
        self.surface = Surface((300, 130)).convert()

        self.surface_inside.fill((255, 255, 255))
        self.surface.fill((0, 0, 0))
        self.font = font.Font(None, 15)
        self.l_font = font.Font(None, 25)

    def update(self, obj=None):
        self.surface_inside.fill((255, 255, 255))
        self.surface.fill((0, 0, 0))
        if obj is not None:
            self.surface_inside.blit(transform.scale(obj.image, (20, 20)), (5, 5))
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

