from pygame import Surface, font

class TowerFrame():
    """ Creates a frame full of information for the selected tower """
    def __init__(self, tower, extra_attributes=None):
        self.tower = tower
        self.image = Surface((200, 300)).convert()
        self.image.fill((200, 115, 0))
        self.s_width = self.image.get_width()
        self.s_height = self.image.get_height()

        # Can't divide by 0
        if self.tower.fire_rate == 0:
            dps_calc = 0
        else:
            dps_calc = self.tower.damage/self.tower.fire_rate

        tower_attributes = {"Name": self.tower.name,
                            "Fire Rate": self.tower.fire_rate,
                            "Damage": self.tower.damage,
                            "DPS": dps_calc,
                            "Damage Done": self.tower.damage_done}
        if extra_attributes is None:
            extra_attributes = dict()
        self.t_attributes = dict(tower_attributes.items() + extra_attributes.items())

        # Upgrades
        self.font = font.Font(None, 18)
        self.upgrade_button = Surface((100, 50)).convert()
        self.upgrade_button.fill((0, 255, 0))
        self.upgrade_button.blit(self.font.render("Upgrade", 1, (0, 0, 0)),
                                 (self.upgrade_button.get_width()/2 - self.font.size("Upgrade")[0]/2,
                                  self.upgrade_button.get_height()/2 - self.font.size("Upgrade")[1]/2))
        self.image.blit(self.upgrade_button, (self.image.get_width() - self.upgrade_button.get_width(),
                                              self.image.get_height() - self.upgrade_button.get_height()))

        level_text = "Level: " + str(self.tower.level)
        self.image.blit(self.font.render(level_text, 1, (0, 0, 0)),
                       (self.image.get_width() - self.upgrade_button.get_width(),
                        self.image.get_height() - self.upgrade_button.get_height() - self.font.size(level_text)[1]))
        self.image.blit(self.tower.image, (self.s_width/2 - self.tower.image.get_width()/2, 2))

        y_value = self.tower.image.get_width() + 7

        # Blits the tower description
        for desc in self.length_splitter(self.font, self.tower.description, self.image.get_width() - 5):
            self.image.blit(self.font.render(desc, 1, (0, 0, 0)), (5, y_value))
            y_value += self.font.get_height() + 1
        y_value += 5

        # Blits the tower's attributes in this order, tacking all extra stuff at the end
        for attr in ["Name", "Fire Rate", "Damage", "DPS", "Damage Done"]+extra_attributes.keys():
            value = self.t_attributes[attr]
            self.image.blit(self.font.render(attr + ": " + str(value), 1, (0, 0, 0)), (5, y_value))
            y_value += self.font.get_height() + 1
        #self.image = OutlinedSurface(self.image, 5).surface

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
