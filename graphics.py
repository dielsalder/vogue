import sys
sys.path.append('./libtcod-1.5.1')
import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45

LIMIT_FPS = 20

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)


class Tile:
    # tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        # by default, if a tile is blocked it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Object:
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        # move by given amount
        if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    def draw(self):
        # set color and draw character at this object's position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        # erase character
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

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

    create_room(Rect(30, 15, 20, 15))
    create_room(Rect(70, 15, 5, 10))
    create_h_tunnel(30, 70, 18)

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

def render_all():
    # draw everything
    for object in objects:
        object.draw()

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = map[x][y].block_sight
            if wall:
                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)

    # blit to root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

def handle_keys():
    global playerx, playery

    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt + Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return True # exit game

    # movement keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        player.move(0, -1)

    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player.move(0, 1)

    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player.move(-1, 0)

    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player.move(1, 0)


libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)

# Create off-screen console
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

libtcod.sys_set_fps(LIMIT_FPS)

make_map()

# initialize player position to center of screen
playerx = SCREEN_WIDTH/2
playery = SCREEN_HEIGHT/2

player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)
npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow)
objects = [npc, player]


# Main loop
# run game as long as window is not closed
while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(con, libtcod.white)

    render_all()

    # "flush" i.e. present changes to screen
    libtcod.console_flush()

    # clear character at last position
    for object in objects:
        object.clear()

    exit = handle_keys()
    if exit:
        break

