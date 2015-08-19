import libtcodpy as libtcod

LIMIT_FPS = 20

# Initialize console
libtcod.console_set_custom_font('consolas10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(screen.SCREEN_WIDTH, screen.SCREEN_HEIGHT, 'python/vogue', False)

# Create off-screen console
con = libtcod.console_new(screen.SCREEN_WIDTH, screen.SCREEN_HEIGHT)

libtcod.sys_set_fps(LIMIT_FPS)

global game_state
game_state = 'playing'

while not libtcod.console_is_window_closed():
    render_all()
    libtcod.console_flush()
