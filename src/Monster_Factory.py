from collections import defaultdict
from src.GameObject import GameObject
from src.Monster import Monster, MonsterGroup
from src.Monster_ai import *
from src.sqlloader import SQLLoader

from copy import deepcopy


class MonsterFactory:
    __instance = None

    @staticmethod
    def get_instance(planet_id):
        if MonsterFactory.__instance is None:
            MonsterFactory.__instance = MonsterFactory(planet_id)
        return MonsterFactory.__instance

    def __init__(self, planet_id):
        self.planet_id = planet_id
        self.sql_loader = SQLLoader.get_instance()
        self.colors = self.sql_loader.load_all_colors()
        self.monsters_list = self.sql_loader.load_monsters_by_planed_id(self.planet_id)
        self.generating_parameters = self.sql_loader.load_monster_generating_parameters_by_planet_id(self.planet_id)
        self.items = self.sql_loader.load_items()

    def load_another_planet(self, planet_id):
        self.planet_id = planet_id
        self.monsters_list = self.sql_loader.load_monsters_by_planed_id(self.planet_id)
        self.generating_parameters = self.sql_loader.load_monster_generating_parameters_by_planet_id(self.planet_id)

    def _generate_monster(self, monster_params, health_potion_prob):
        monster = Monster(monster_params['name'], monster_params['hp'], monster_params['defense'],
                          monster_params['power'], monster_params['accuracy'], monster_params['evading'],
                          randint(0, monster_params['max_money']), monster_params['chance_to_attack'],
                          monster_params['defense_addition'], deepcopy(monster_params['skills']),
                          monster_params['fighting_image'], monster_params['fighting_image_chosen'])

        if randint(0, 100) < health_potion_prob:
            monster.add_item_to_inventory(self.items[0])  # TODO: make it more random and not just health potion

        return monster

    def generate_monster_group(self, game_map):
        while True:
            x = randint(0, game_map.map_width - 1)
            y = randint(0, game_map.map_height - 1)
            if not game_map.field[x][y].is_part_of_village and not game_map.field[x][y].is_blocked:
                break

        number_of_monsters_in_group = randint(1, self.generating_parameters['max_monsters_in_group'])
        monsters = []
        monster_icons = defaultdict(int)

        max_value = 0
        iconmax = ''
        for i in range(0, number_of_monsters_in_group):
            monster_params = self.monsters_list[randint(0, len(self.monsters_list) - 1)]
            monster = self._generate_monster(monster_params, 100 - self.generating_parameters['peaceful_prob'])
            monsters.append(monster)

            # search for most frequent icon
            icon = monster_params['icon']
            monster_icons[icon] += 1
            if monster_icons[icon] > max_value:
                iconmax = icon

        color = None
        name = ''
        for monster in self.monsters_list:
            if monster['icon'] == iconmax:
                color = monster['color']
                name = monster['name']
                break

        monster_group_game_object = GameObject(x, y, iconmax, self.colors[color], 'monster', name)

        if randint(0, 100) < self.generating_parameters['peaceful_prob']:
            monster_ai = PeacefulAi()
        else:
            monster_ai = AggressiveAi(self.generating_parameters['aggresive_ai_attack_radius'])

        monster_group = MonsterGroup(monster_group_game_object, monster_ai, monsters)

        return monster_group_game_object, monster_group
