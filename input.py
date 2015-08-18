def handle_keys():
    global fov_recompute
    global key
    #libtcod.sys_wait_for_event(1, key, None, True)
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
            # other keys
            key_char = chr(key.c)

            if key_char == 'g':
                # pick up an item
                for object in objects:
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'd':
                chosen_item = inventory_menu('Drop which item?')
                if chosen_item is not None:
                    chosen_item.drop()

            return 'didnt-take-turn'

