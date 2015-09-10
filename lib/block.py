from pygame import sprite, Surface, Rect

class Block(sprite.Sprite):
    """ Base Block Class """
    def __init__(self, pos, is_end):
        sprite.Sprite.__init__(self)
        self.pos = pos
        self.grid_pos = tuple([x/40 for x in self.pos])
        self.image = Surface((40, 40)).convert()
        self.color = (125, 125, 125)
        self.image.fill((255, 255, 255))
        self.rect = Rect(self.pos, self.image.get_size())
        self.is_shown = False
        self.is_path = False
        self.neighbors = set()
        self.path_value = 0
        self.is_end = is_end

    def get_neighbors(self, lst):
        for b in lst:
            if self in b:
                a = self

                # Left
                if b.index(a) != 0:
                    to_add = b[b.index(a)-1]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(b[b.index(a)-1])

                # Right
                if b.index(a) != len(b)-1:
                    to_add = b[b.index(a)+1]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(b[b.index(a)+1])

                # Above
                if lst.index(b) != 0:
                    to_add = lst[lst.index(b)-1][b.index(a)]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(lst[lst.index(b)-1][b.index(a)])

                # Below
                if lst.index(b) != len(lst)-1:
                    to_add = lst[lst.index(b)+1][b.index(a)]
                    if to_add != self and not to_add.is_shown:
                        self.neighbors.add(lst[lst.index(b)+1][b.index(a)])

