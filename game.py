import libtcodpy as libtcod
import entity
import gamemap
import gui
import textwrap

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

LIMIT_FPS = 20

FOV_ALGO = 0    # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

def init_player():
    fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
    player = entity.Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)

def init_world():
    # objects = [player]
    inventory = []
    global map
    map = gamemap.make_map()

def init_display():
    # Set up display
    libtcod.console_set_custom_font('consolas10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/vogue', False)

    # Create off-screen console
    global con
    con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

    libtcod.sys_set_fps(LIMIT_FPS)

def init_fov():
    global fov_map
    fov_map = libtcod.map_new(gamemap.MAP_WIDTH, gamemap.MAP_HEIGHT)
    for y in range(gamemap.MAP_HEIGHT):
        for x in range(gamemap.MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
    global fov_recompute
    fov_recompute = True

def render_game():
    #global fov_map
    # draw everything
    #global fov_recompute

   # for object in objects:
   #     if object != player:
   #         object.draw()
   # # player is always drawn last i.e. on top
   # player.draw()

    for y in range(gamemap.MAP_HEIGHT):
        for x in range(gamemap.MAP_WIDTH):
            #visible = libtcod.map_is_in_fov(fov_map, x, y)
            visible = True
            wall = map[x][y].block_sight
            if not visible:
                if map[x][y].explored:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, gamemap.color_dark_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, gamemap.color_dark_ground, libtcod.BKGND_SET)
            else:
                if wall:
                    libtcod.console_set_char_background(con, x, y, gamemap.color_light_wall, libtcod.BKGND_SET)
                else:
                    libtcod.console_set_char_background(con, x, y, gamemap.color_light_ground, libtcod.BKGND_SET)
                map[x][y].explored = True

   #if fov_recompute:
   #    # recompute FOV if needed
   #    fov_recompute = False
   #    libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

    # blit to root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


def render_gui():
    # HUD offscreen console
    panel = libtcod.console_new(SCREEN_WIDTH, gui.PANEL_HEIGHT)

    # render HUD
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)
   #gui.render_bar(1, 1, gui.BAR_WIDTH, gui.BAR_HEIGHT, 'HP',
   #        player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)

    # List of messages
    global game_msgs
    game_msgs = []

    # message log
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, gui.PANEL_HEIGHT, 0, 0, gui.PANEL_Y)

    gui.message('Welcome to the kobold hole.', libtcod.green)

def message(new_msg, color = libtcod.white):
    # split message if necessary
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
        game_msgs.append( (line, color) )

def render_all():
    render_game()
    render_gui()

def start_game():
    game_state = "playing"
    global player_action
    player_action = None

    key = libtcod.Key()
    mouse = libtcod.Mouse()

def run_game():
    # main loop
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():

        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)

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
                if object.ai:
                    object.ai.take_turn()
