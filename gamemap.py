import math
import libtcodpy as libtcod

MAP_WIDTH = 80
MAP_HEIGHT = 45

MAX_ROOM_MONSTERS = 5
MAX_ROOM_ITEMS = 2

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

class Tile:
    # tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.explored = False
        self.blocked = blocked

        # by default, if a tile is blocked it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect:
    # a rectangle on the map, used for a room
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
        # does it intersect with anything?
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

def create_room(room):
    global map
    # go through tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def make_map():
    global map

    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30
    # fill map with "blocked" tiles
    map = [[ Tile(True)
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

            # add contents
           #place_objects(new_room)

            (new_x, new_y) = new_room.center()
            # print "room number" to see drawing order
            #room_no = Object(new_x, new_y, chr(65+num_rooms), 'room number', libtcod.white)
            #objects.insert(0, room_no)  # draw first, so monsters are on top

           #if num_rooms == 0:
           #    # if this is the first room, where player starts
           #    player.x = new_x
           #    player.y = new_y

            if num_rooms > 0:
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
    return map

def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
