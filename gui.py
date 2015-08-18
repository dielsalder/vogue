import libtcodpy as libtcod
import textwrap

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

INVENTORY_WIDTH = 50
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
BAR_WIDTH = 20
BAR_HEIGHT = 1
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1


def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options')

    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    height = len(options) + header_height

    window = libtcod.console_new(width, height)

    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height,
            libtcod.BKGND_NONE, libtcod.LEFT, header)

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    # last two parameters: foreground and background opacity
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #libtcod.flush = True
    libtcod.console_flush()
    #key = libtcod.wait_for_event(key, True)
    # flushes second event from handle_keys
    libtcod.console_wait_for_keypress(True)
    key = libtcod.console_wait_for_keypress(True)

    # return option
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def inventory_menu(header):
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory]

    index = menu(header, options, INVENTORY_WIDTH)

    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def render_bar(x, y, w, h, name, value, maximum, bar_color, back_color):
    # width of bar on screen
    bar_width = (w * value) / maximum

    # render background
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, w, h, False, libtcod.BKGND_SCREEN)

    # render bar
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, h,
                False, libtcod.BKGND_SCREEN)

    # render label
    label = name + ": " + str(value) + "\/" + str(maximum)
    libtcod.console_set_default_foreground(panel, libtcod.white)
    # (console, x, y, background flag, alignment, string)
    libtcod.console_print_ex(panel, x + w / 2, y,
            libtcod.BKGND_NONE, libtcod.CENTER, label)

