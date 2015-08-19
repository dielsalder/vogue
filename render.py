import libtcodpy as libtcod
import screen
import game_map

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

libtcod.console_set_custom_font('consolas10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/kobold hole', False)

con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

def draw_map(con):
    """ Draw all map tiles """
    for y in range(game_map.MAP_HEIGHT):
        for x in range(game_map.MAP_WIDTH):
            tile = game_map.level_map[x][y]
            tile.drawer.draw(con, x, y)

def display(con):
    """
    Display con on root console
    Blit con to root console, then flush
    """
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    libtcod.console_flush()

def draw_all():
    draw_map(con)
    display()
