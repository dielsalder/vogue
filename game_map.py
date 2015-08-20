import libtcodpy as libtcod
import screen

MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

global level_map

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

class Tile:
    """
    Properties of a map tile
    """
    def __init__(self, blocked, drawer, block_sight = None):
        self.explored = False
        self.blocked = blocked

        # by default, if a tile is blocked it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

        self.drawer = drawer
        drawer.owner = self

class Rect:
    """ A rectangle on the map, used for a room """
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        """ Check for intersection with another rectangle """
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class TileDrawer:
    """
    Draws a tile; component of Tile
    Map passes x, y and this to renderer function
    """

    def __init__(self, color_light, color_dark):
        self.color_light = color_light
        self.color_dark = color_dark

    def draw(self, con, x, y):
        # todo: add check for FOV, explored
        libtcod.console_set_char_background(con, x, y, self.color_light)



def create_room(room):
    global level_map
    # go through tiles in the rectangle and make them floor
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            level_map[x][y] = floor

def make_map():
    global level_map

    # fill map with rock
    level_map = [[ rock
        for y in range(MAP_HEIGHT)]
            for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        # 0 identifies "stream" to get random number from
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
        new_room = Rect(x, y, w, h)

        # interesting
        failed = False
        # check for intersections
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            # no intersections, room is valid

            create_room(new_room)

            (new_x, new_y) = new_room.center()
            # print "room number" to see drawing order
            #room_no = Object(new_x, new_y, chr(65+num_rooms), 'room number', libtcod.white)
            #objects.insert(0, room_no)  # draw first, so monsters are on top

            if num_rooms == 0:
                # if this is the first room, where player starts
               #player.x = new_x
               #player.y = new_y
                pass

            else:
                # other rooms exist
                # connect to previous rooms with tunnel

                # center crds of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                # draw a coin
                if libtcod.random_get_int(0, 0, 1) == 1:
                    # first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)

                else:
                    # first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            rooms.append(new_room)
            num_rooms += 1
    return level_map

def create_h_tunnel(x1, x2, y):
    global level_map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        level_map[x][y] = hallway_floor

def create_v_tunnel(y1, y2, x):
    global level_map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        level_map[x][y] = hallway_floor

def is_blocked(x, y):
    # test map tile
    if level_map[x][y].blocked:
        return True
    return False

#def place_objects(room):
#    place_monsters(room)
#    place_items(room)

def place_monsters(room):
    # choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    # place monster
    for n in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked(x, y):
            if libtcod.random_get_int(0, 0, 100) <= 60:
                fighter_component = Fighter(hp=10, defense=0, power=3, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'd', 'dog', libtcod.desaturated_green,
                        blocks = True, fighter=fighter_component, ai=ai_component)

            else:
                fighter_component = Fighter(hp=16, defense=0, power=3)
                ai_component = BasicMonster()
                monster = Object(x, y, 'T', 'tiger', libtcod.desaturated_green,
                        blocks = True, fighter=fighter_component, ai=ai_component)

            num_monsters += 1

def place_items(room):
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)
    for i in range(num_items):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked (x, y):
            item_component = Item(use_function = cast_heal)
            item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)

            objects.append(item)
            item.send_to_back()

# Data: tile types
# todo: store externally
default_drawer = TileDrawer(libtcod.red, libtcod.red)

rock_drawer = TileDrawer(color_light_wall, color_dark_wall)
rock = Tile(True, rock_drawer)

wall = rock

floor_drawer = TileDrawer(color_light_ground, color_dark_ground)
floor = Tile(False, floor_drawer, block_sight = False)

hallway_floor = floor
room_floor = floor
