class Object:
    def __init__(self, x, y, char, name, color, blocks = False, fighter=None, ai=None,
            item=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks    # does this block movement

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self # let component know owner

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

    def move(self, dx, dy):
        # move by given amount
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        # vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def draw(self):
        # set color and draw character at this object's position
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def send_to_back(self):
        # make this object be drawn first, so all others appear above it
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def is_visible(self):
        return libtcod.map_is_in_fov(fov_map, self.x, self.y)

    def clear(self):
        # erase character
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

class Fighter:
    # combat related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, death_function=None):
        self.max_hp = hp
        self.hp = self.max_hp
        self.defense = defense
        self.power = power
        self.death_function = death_function

    def take_damage(self, damage):
        if self.hp > 0:
            self.hp -= damage

            # check for death - if there's a death function, call it
            if self.hp<= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)

    def attack(self, target):
        damage = self.power - target.fighter.defense
        if damage > 0:
            message("The " + self.owner.name + " attacks the " + target.name + "!")
            target.fighter.take_damage(damage)
        else:
            message("The " + self.owner.name + "'s attack bounces off!")

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

class BasicMonster:
    # AI for a basic monster
    def take_turn(self):
        monster = self.owner

        if monster.is_visible():
            # move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)

            # attack if player is still alive + close enough
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

class PlayerAI:
    # controls things that happen to the player on each turn
    def take_turn(self):
        player = player
        pass

class Item:
    # item that can be picked up and used
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self):
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up the ' + self.owner.name)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '.')

    def use(self):
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                # destroy after use, unless it was canceled
                inventory.remove(self.owner)

    def drop(self):
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.')


def player_move_or_attack(dx, dy):
    global fov_recompute

    # coordinates player is moving to or attacking
    x = player.x + dx
    y = player.y + dy

    # try to find an attackable object there
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    # attack if target found, move otherwise
    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True

# Death

def player_death(player):
    # game over
    player.char = '%'

    global game_state
    game_state = 'dead'
    message( 'You died!')


def monster_death(monster):
    message( "The " + monster.name + " dies!")
    monster.char = '%'
    monster.ai = None
    monster.blocks = False
    monster.fighter = None
    monster.name = monster.name + ' corpse'
    monster.send_to_back()

def cast_heal():
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.')
        return cancelled

    heal_hp = player.fighter.max_hp / 5
    message('You feel your wounds healing.', libtcod.light_violet)
    player.fighter.heal(heal_hp)

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
    place_monsters(room)
    place_items(room)

def place_monsters(room):
    # choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    # place monster
    for n in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked(x, y):
            if libtcod.random_get_int(0, 0, 100) <= 60:
                fighter_component = Fighter(hp=10, defense=0, power=3, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green,
                        blocks = True, fighter=fighter_component, ai=ai_component)

            else:
                fighter_component = Fighter(hp=16, defense=0, power=3)
                ai_component = BasicMonster()
                monster = Object(x, y, 'T', 'troll', libtcod.desaturated_green,
                        blocks = True, fighter=fighter_component, ai=ai_component)

            num_monsters += 1
            objects.append(monster)

def place_items(room):
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)
    for i in range(num_items):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked (x, y):
            item_component = Item(use_function = cast_heal)
            item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)

            objects.append(item)
            item.send_to_back()
