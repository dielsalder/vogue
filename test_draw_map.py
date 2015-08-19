import libtcodpy as libtcod
import render
import game_map

game_map.make_map()
render.draw_map(render.con)
render.display(render.con)

a = input()
