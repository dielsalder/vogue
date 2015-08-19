import libtcodpy as libtcod
import render
import game_map
import entity

potion_drawer = entity.EntityDrawer("!", libtcod.violet)
potion = entity.Entity(20, 20, 'potion', potion_drawer)
entity.entities = [potion]

game_map.make_map()
render.draw_map(render.con)
render.draw_entities(render.con)
render.display(render.con)

a = input()
