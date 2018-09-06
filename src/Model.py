from src.sqlloader import SQLLoader
from src.Map import *
from src.GameObject import GameObject
from src.Monster_Factory import MonsterFactory


class Model:
    def __init__(self, field_width, field_height, map_width, map_height):

        self.field_width = field_width
        self.field_height = field_height
        self.map_width = map_width
        self.map_height = map_height
        self.loader = SQLLoader.get_instance()

        self.colors = self.loader.load_loadup_colors()
        self.planet_id = 1
        self.planets = None
        self.planet_parameters = None

        self.map = None
        self.objects = None
        self.monster_groups = None
        self.visible_field = None

        self.fight_just_started = False
        self.enemy = None
        self.chosen_monster_index = 0
        self.accumulated_reward = None

        self.monster_factory = MonsterFactory.get_instance(self.planet_id)
        player_game_object = GameObject(self.field_width // 2, self.field_height // 2, '@', self.colors['white'],
                                        'player')

        self.player = self.loader.load_player(player_game_object)
        self.load_new_planet()

    def load_new_planet(self):
        self.planets = self.loader.load_planet_parameters()
        self.planet_parameters = self.planets[self.planet_id - 1]
        self.loader.load_planet_colors_by_id(self.planet_id, self.colors)
        self.monster_factory.load_another_planet(self.planet_id)

        map_gen = MapGenerator(self.field_width, self.field_height, self.map_width, self.map_height,
                               self.planet_id, self.planet_parameters['number_of_monster_groups'])

        self.map, self.objects, self.monster_groups = map_gen.generate(self.planet_parameters)
        self.visible_field = self.map.get_first_visible_field(self.field_width // 2, self.field_height // 2)
        self.objects.append(self.player.game_object)

    def monster_turn(self, presenter):
        for monster_group in self.monster_groups:
            monster_group.make_a_move(presenter)

    def player_move_or_attack(self, dx, dy, presenter):
        # the coordinates the player is moving to/attacking
        x = self.player.game_object.x + dx
        y = self.player.game_object.y + dy
        self.visible_field = self.map.update_visible_field(dx, dy)

        # try to find an attackable object there
        target = None
        for obj in self.objects:
            if obj.x == x and obj.y == y:
                target = obj
                break

        # attack if target found, move otherwise
        if target is not None:
            self.start_fight(target.owner, presenter)
        else:
            self.player.game_object.move(dx, dy, self.map)

    def start_fight(self, target, presenter):
        presenter.game_state = 'fighting'
        presenter.fight_state = 'choosing action'
        self.fight_just_started = True
        self.enemy = target
        self.chosen_monster_index = 0
        presenter.previous_arrow = 'right'
        self.accumulated_reward = {'xp': 0, 'money': 0, 'inventory': []}

    def get_objects(self):
        return self.objects

    def get_player(self):
        return self.player

    def get_map(self):
        return self.map

    def get_enemy(self):
        return self.enemy

    def get_monster_groups(self):
        return self.monster_groups

    def get_visible_field(self):
        return self.visible_field
