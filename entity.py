import libtcodpy as libtcod

MAX_ITEMS = 20

class Entity:
    """ Any object (player, NPCs, items, dungeon features """
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

def generate_items():
    """
    Generate list of all items on level which is passed to place_items
    can expand to gen_potions(), gen_monsters(), etc
    """

    global items

# data
player_drawer = EntityDrawer("@", libtcod.white)
player = Entity(40, 40, 'player', player_drawer, blocks = True)

global entities
entities = []

global items
items = []
