import libtcodpy as libtcod
import render
import game_map
import entity

game_map.make_map()
render.draw_map(render.con)
entity.populate_items(game_map.level_map)

render.draw_items(render.con)
render.display(render.con)

a = input()
