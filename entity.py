import libtcodpy as libtcod

class Entity:
    """ Any object (player, NPCs, items, dungeon feature s"""
    def __init__(self, x, y, name, drawer, blocks = False):
        self.x = x
        self.y = y
        self.name = name
        drawer.owner = self
        self.drawer = drawer

class EntityDrawer:
    """
    Draws an entity; component of Entity
    """
    def __init__(self, char, fg, bg = None):
        self.char = char
        self.fg = fg
        self.bg = bg

    def draw(self, con):
        x = self.owner.x
        y = self.owner.y
        if self.bg:
            libtcod.console_set_char_background(con, x, y, self.fg)
        libtcod.console_set_default_foreground(con, self.fg)
        libtcod.console_put_char(con, x, y, self.char, libtcod.BKGND_NONE)

# data
player_drawer = EntityDrawer("@", libtcod.white)
player = Entity(0, 0, 'player', player_drawer, blocks = True)

entities = []
