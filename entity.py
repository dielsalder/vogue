import libtcodpy as libtcod
import game_map

MAX_LEVEL_ITEMS = 20

class Entity:
    """ Any object (player, NPCs, items, dungeon features """
    def __init__(self, name, drawer, blocks = False):
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

class Item(Entity):
    def __init__(self, name, drawer, blocks = False):
        self.name = name
        drawer.owner = self
        self.drawer = drawer

def generate_items(max_items):
    """
    Generate list of all items on level which is passed to place_items
    can expand to gen_potions(), gen_monsters(), etc
    """
    items = []
    d = 5       # greatest possible difference from max
    num_items = libtcod.random_get_int(0, max_items - d, max_items)
    for i in range(num_items):
        item = garbage
        items.append(item)
        print "Generated item: " + item.name
    return items

def place_items(unplaced_items, level_map):
    global items
    """
    Place items randomly into allowed map cells
    """

    for item in unplaced_items:
        # Find a map cell where an item can be placed
        allowed = False
        while allowed == False:
            x = libtcod.random_get_int(0, 1, game_map.MAP_WIDTH - 1)
            y = libtcod.random_get_int(0, 1, game_map.MAP_HEIGHT - 1)
            # Not in hallways, please
            allowed = level_map[x][y] == game_map.floor
            print allowed

        item.x = x
        item.y = y
        items.append(item)
        print "Placed item: " + item.name

def populate_items(level_map):
    """ Populate level map with items """
    new_items = generate_items(MAX_LEVEL_ITEMS)
    place_items(new_items, game_map.level_map)

global entities
entities = []

global items
items = []

global actors
actors = []

# data
player_drawer = EntityDrawer("@", libtcod.white)
player = Entity('player', player_drawer, blocks = True)

garbage_drawer = EntityDrawer("%", libtcod.dark_violet)
garbage = Entity('garbage', garbage_drawer, blocks = False)
