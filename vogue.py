import sys
sys.path.append('./libtcod-1.5.1')
import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45

LIMIT_FPS = 20

FOV_ALGO = 0    # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

MAX_ROOM_MONSTERS = 5

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

class Object:
    def __init__(self, x, y, char, name, color, blocks = False):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks    # blocks movement?

    def move(self, dx, dy):
        # move by given amount
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def draw(self):
        # set color and draw character at this object's position
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
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
            place_objects(new_room)

            (new_x, new_y) = new_room.center()
            # print "room number" to see drawing order
            room_no = Object(new_x, new_y, chr(65+num_rooms), 'room number', libtcod.white)
            objects.insert(0, room_no)  # draw first, so monsters are on top

            if num_rooms == 0:
                # if this is the first room, where player starts
                player.x = new_x
                player.y = new_y

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

def is_blocked(x, y):
    # test map tile
    if map[x][y].blocked:
        return True

    # check for blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def place_objects(room):
    # choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    # place monster
    for n in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)

        if not is_blocked(x, y):
            if libtcod.random_get_int(0, 0, 100) <= 80:
                monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks = True)

            else:
                monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks = True)

            num_monsters += 1
            objects.append(monster)

def render_all():
    # draw everything
    global fov_recompute

    for object in objects:
        object.draw()

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            visible = libtcod.map_is_in_fov(fov_map, x, y)
            wall = map[x][y].block_sight
            if not visible:
                if map[x][y].explored:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
            else:
                if wall:
                    libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET)
                else:
                    libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)
                map[x][y].explored = True

    if fov_recompute:
        # recompute FOV if needed
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

    # blit to root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

def handle_keys():
    global fov_recompute
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt + Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit' # exit game

    if game_state == 'playing':
        # movement keys
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            player_move_or_attack(0, -1)
            fov_recompute = True

        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            player_move_or_attack(0, 1)
            fov_recompute = True

        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            player_move_or_attack(-1, 0)
            fov_recompute = True

        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            player_move_or_attack(1, 0)
            fov_recompute = True

        else:
            return 'didnt-take-turn'

def player_move_or_attack(dx, dy):
    global fov_recompute

    # coordinates player is moving to or attacking
    x = player.x + dx
    y = player.y + dy

    # try to find an attackable object there
    target = None
    for object in objects:
        if object.x == x and object.y == y:
            target = object
            break

    # attack if target found, move otherwise
    if target is not None:
        print "The " + target.name + " laughs at your puny effort to attack her!"
    else:
        player.move(dx, dy)
        fov_recompute = True

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/vogue', False)

# Create off-screen console
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

libtcod.sys_set_fps(LIMIT_FPS)

player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', 'player', libtcod.white, blocks = True)
objects = [player]

make_map()

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
global fov_recompute
fov_recompute = True

global game_state
game_state = "playing"
global player_action
player_action = None

# Main loop
while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(con, libtcod.white)

    render_all()

    # "flush" i.e. present changes to screen
    libtcod.console_flush()

    # clear character at last position
    for object in objects:
        object.clear()

    player_action = handle_keys()
    if player_action == 'exit':
        break

    if game_state == 'playing' and player_action != 'didnt-take-turn':
        for object in objects:
            if libtcod.map_is_in_fov(fov_map, object.x, object.y):
                if object != player:
                    print 'The ' + object.name + ' growls!'
