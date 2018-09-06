import sqlite3
from src.Item import Item
from src.Player import Player

database_name = 'game'


class SQLLoader:

    __instance = None

    @staticmethod
    def get_instance():
        if SQLLoader.__instance is None:
            SQLLoader.__instance = SQLLoader()
        return SQLLoader.__instance

    def __init__(self):
        self.game_conn = sqlite3.connect('game.db')
        self.c = self.game_conn.cursor()

    def load_items(self):
        items = []
        for item_attr in self.c.execute('SELECT * FROM items'):
            item = Item(item_attr[1], item_attr[2], item_attr[3], item_attr[4],
                        item_attr[5], item_attr[6], item_attr[7]/100.0, item_attr[8])
            items.append(item)
        return items

    def load_monsters_by_planed_id(self, planet_id):
        monsters = []

        self.c.execute('SELECT * FROM enemies WHERE planet_id=?', (planet_id, ))
        for monster_attr in self.c.fetchall():
            monster_skills = set()
            monster_id = (monster_attr[0],)
            for monster_skill in self.c.execute('SELECT * FROM enemy_skills WHERE monster_id=?', monster_id):

                # TODO:
                # actually change it to skills
                skill = Item(monster_skill[2], monster_skill[3], monster_skill[4], monster_skill[5],
                             monster_skill[6], monster_skill[7], monster_skill[8]/100.0, monster_skill[9])
                monster_skills.add(skill)

            monster = {'name': monster_attr[2], 'hp': monster_attr[3], 'defense': monster_attr[4],
                       'power': monster_attr[5], 'accuracy': monster_attr[6], 'evading': monster_attr[7],
                       'color': monster_attr[8], 'icon': monster_attr[9], 'fighting_image': monster_attr[10],
                       'max_money': monster_attr[11], 'chance_to_attack': monster_attr[12],
                       'defense_addition': monster_attr[13], 'skills': monster_skills,
                       'fighting_image_chosen': monster_attr[14]}
            monsters.append(monster)

        return monsters

    def load_player_skills(self):
        skills = []
        for skill_attr in self.c.execute('SELECT * FROM player_skills'):

            # TODO:
            # actually change it to skills
            skill = Item(skill_attr[1], skill_attr[2], skill_attr[3], skill_attr[4],
                         skill_attr[5], skill_attr[6], skill_attr[7], skill_attr[8])
            skills.append(skill)
        return skills

    def load_planet_parameters(self):
        planet_parameters = self.c.execute('SELECT * FROM planets_parameters').fetchall()
        planets = []
        for planet_parameters in planet_parameters:
            parameters = {'grass_prob': planet_parameters[2], 'sand_prob': planet_parameters[3],
                          'grass_cluster_prob': planet_parameters[4], 'sand_cluster_prob': planet_parameters[5],
                          'min_distance_between_clusters': planet_parameters[6],
                          'max_grass_cluster_radius': planet_parameters[7],
                          'max_sand_cluster_radius': planet_parameters[8],
                          'added_prob_near_grass': planet_parameters[9],
                          'added_prob_near_sand': planet_parameters[10], 'village_radius': planet_parameters[11],
                          'k_neighbors': planet_parameters[12], 'number_of_monster_groups': planet_parameters[15],
                          'money_to_travel_to_next_planet': planet_parameters[16]}

            planets.append(parameters)

        return planets

    def load_planet_colors_by_id(self, planet_id, colors):
        planet_parameters = self.c.execute('SELECT * FROM planets_parameters WHERE id=?', (planet_id, )).fetchone()
        grass_color_parameters = self.c.execute('SELECT * FROM colors WHERE id=?',
                                                (planet_parameters[13],)).fetchone()
        colors['grass_color'] = (grass_color_parameters[2], grass_color_parameters[3], grass_color_parameters[4])

        sand_color_parameters = self.c.execute('SELECT * FROM colors WHERE id=?',
                                               (planet_parameters[14],)).fetchone()
        colors['sand_color'] = (sand_color_parameters[2], sand_color_parameters[3], sand_color_parameters[4])

    def load_loadup_colors(self):
        colors = {}
        all_loadup_colors = self.c.execute('SELECT * FROM loadup_colors').fetchall()
        for loadup_colors in all_loadup_colors:
            color_id = (loadup_colors[2], )
            color_parameters = self.c.execute('SELECT * FROM colors WHERE id=?', color_id).fetchone()
            colors[loadup_colors[1]] = (color_parameters[2], color_parameters[3], color_parameters[4])
        return colors

    def load_all_colors(self):
        colors = {}
        for color_parameter in self.c.execute('SELECT * FROM colors').fetchall():
            colors[color_parameter[1]] = (color_parameter[2], color_parameter[3], color_parameter[4])

        return colors

    def load_monster_generating_parameters_by_planet_id(self, planet_id):
        planet_parameters = self.c.execute('SELECT * FROM generating_parameters WHERE planet_id=?',
                                           (planet_id,)).fetchone()

        parameters = {'max_monsters_in_group': planet_parameters[2], 'peaceful_prob': planet_parameters[3],
                      'aggresive_ai_attack_radius': planet_parameters[4]}

        return parameters

    def load_player(self, game_object):
        player_parameters = self.c.execute('SELECT * FROM player_parameters').fetchone()
        player = Player(game_object, player_parameters[1], player_parameters[2], player_parameters[3],
                        player_parameters[4], player_parameters[5], player_parameters[6], player_parameters[7],
                        player_parameters[8], player_parameters[9], player_parameters[10], player_parameters[11],
                        player_parameters[12], player_parameters[13])
        player_skills = self.load_player_skills()
        for skill in player_skills:
            player.add_item_to_inventory(skill)
        items = self.load_items()
        player.add_item_to_inventory(items[0])
        player.add_item_to_inventory(items[1])
        return player

    def load_gui_settings(self):
        gui_parameters = self.c.execute('SELECT * FROM gui_settings').fetchone()
        gui_settings = {'screen_width': gui_parameters[1], 'screen_height': gui_parameters[2],
                        'map_screen_width': gui_parameters[3], 'map_screen_height': gui_parameters[4],
                        'bar_width': gui_parameters[5], 'panel_height': gui_parameters[6], 'panel_y': gui_parameters[7],
                        'msg_x': gui_parameters[8], 'msg_width': gui_parameters[9], 'msg_height': gui_parameters[10],
                        'fighting_msg_width': gui_parameters[11], 'fighting_panel_height': gui_parameters[12],
                        'fighting_panel_y': gui_parameters[13], 'fighting_msg_indent': gui_parameters[14],
                        'fighting_msg_height': gui_parameters[15], 'actions': gui_parameters[16].split(','),
                        'fps_limit': gui_parameters[17]}

        return gui_settings

    def load_map_field_parameters(self):
        field_parameters = self.c.execute('SELECT * FROM map_field_parameters').fetchone()
        map_field_parameters = {'map_width': field_parameters[1], 'map_height': field_parameters[2]}
        return map_field_parameters
