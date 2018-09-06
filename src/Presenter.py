from tcod import image_load
from src.sqlloader import SQLLoader
from src.Model import Model
import textwrap
import os.path


class Presenter:
    def __init__(self, root, con, panel, fighting_panel):
        self.root = root
        self.con = con
        self.panel = panel
        self.fighting_panel = fighting_panel

        self.game_state = 'playing'
        self.fight_state = 'not fighting'

        self.game_msgs = []
        self.fighting_msgs = []
        self.monster_groups = []
        self.planet_id = 1

        self.loader = SQLLoader.get_instance()

        self.colors = self.loader.load_loadup_colors()
        self.planets = None
        self.planet_parameters = None
        self.load_new_planet()

        self.gui_settings = self.loader.load_gui_settings()
        self.map_field_parameters = self.loader.load_map_field_parameters()

        self.model = Model(self.map_field_parameters['map_width'], self.map_field_parameters['map_height'],
                           self.gui_settings['map_screen_width'], self.gui_settings['map_screen_height'])

        self.previous_arrow = 'right'

    def load_new_planet(self):
        self.planets = self.loader.load_planet_parameters()
        self.planet_parameters = self.planets[self.planet_id - 1]
        self.loader.load_planet_colors_by_id(self.planet_id, self.colors)

    def render(self):
        if self.game_state == 'playing':
            self.model.monster_turn(self)
            self.render_all_roguelike()

            for obj in self.model.get_objects():
                obj.clear(self.con)
        else:
            self.render_all_fighting()

    def render_all_roguelike(self):
        # go through all tiles, and set their background color
        self.con.clear()
        visible_field = self.model.get_visible_field()
        for y in range(self.gui_settings['map_screen_height']):
            for x in range(self.gui_settings['map_screen_width']):
                block_type = visible_field[x][y].get_type()
                if block_type == 'sand':
                    self.con.draw_char(x, y, None, fg=None, bg=self.colors['sand_color'])
                else:
                    self.con.draw_char(x, y, None, fg=None, bg=self.colors['grass_color'])

        player = self.model.get_player()

        # draw all objects in the list
        for obj in self.model.get_objects():
            obj.draw(self.con, player.game_object.x, player.game_object.y, self.model.get_map())

        self.root.blit(self.con, 0, 0, self.gui_settings['screen_width'], self.gui_settings['screen_height'], 0, 0)

        # prepare to render the GUI panel
        self.panel.clear(fg=self.colors['white'], bg=self.colors['black'])

        # print the game messages, one line at a time
        y = 1
        for (line, color) in self.game_msgs:
            self.panel.draw_str(self.gui_settings['msg_x'], y, line, bg=None, fg=color)
            y += 1

        # show the player's stats
        self.render_bar(1, 0, self.gui_settings['bar_width'], 'PLAYER', -1, -1,
                        self.colors['black'], self.colors['black'], self.panel)

        self.render_bar(1, 1, self.gui_settings['bar_width'], 'HP', player.hp, player.max_hp,
                        self.colors['hp_ft'], self.colors['hp_bg'], self.panel)

        self.render_bar(1, 2, self.gui_settings['bar_width'], 'XP', player.xp, player.max_xp,
                        self.colors['xp_ft'], self.colors['xp_bg'], self.panel)

        self.render_bar(1, 4, self.gui_settings['bar_width'],
                        f'{player.money}/{self.planet_parameters["money_to_travel_to_next_planet"]} gold', -1, -1,
                        self.colors['black'], self.colors['black'], self.panel)

        self.render_bar(1, 5, self.gui_settings['bar_width'], 'until next planet', -1, -1,
                        self.colors['black'], self.colors['black'], self.panel)

        self.root.blit(self.panel, 0, self.gui_settings['panel_y'],
                       self.gui_settings['screen_width'], self.gui_settings['panel_height'], 0, 0)

    def render_all_fighting(self):

        if self.model.fight_just_started:
            self.model.fight_just_started = False

        self.con.clear(fg=self.colors['white'], bg=self.colors['black'])

        self.fighting_panel.clear(fg=self.colors['white'], bg=self.colors['black'])

        player = self.model.get_player()
        enemy = self.model.get_enemy()
        chosen_monster = None

        # in case we killed the last one in the list
        if self.model.chosen_monster_index >= len(self.model.enemy.monsters):
            self.model.chosen_monster_index = len(self.model.enemy.monsters) - 1

        if len(self.model.enemy.monsters) > 0:
            chosen_monster = enemy.monsters[self.model.chosen_monster_index]
            self.render_monsters_screen(enemy.monsters, self.con, self.model.chosen_monster_index,
                                        self.previous_arrow)

        self.root.blit(self.con, 0, 0, self.gui_settings['screen_width'], self.gui_settings['screen_height'], 0, 0)

        if self.fight_state == 'choosing action':
            x = 1
            for action in self.gui_settings['actions']:
                self.render_bar(x, 1, self.gui_settings['fighting_msg_width'], action, -1, -1,
                                self.colors['black'], self.colors['black'], self.fighting_panel)
                x += self.gui_settings['fighting_msg_width'] + self.gui_settings['fighting_msg_indent']

        elif self.fight_state == 'choosing weapon':
            weapons = player.get_weapons()

            x = 1
            i = 1
            for weapon in weapons:
                self.render_bar(x, 1, self.gui_settings['fighting_msg_width'], f'{i}: {weapon.name}', -1, -1,
                                self.colors['black'], self.colors['black'], self.fighting_panel)
                x += self.gui_settings['fighting_msg_width'] + self.gui_settings['fighting_msg_width']
                i += 1
            self.render_bar(x, 1, self.gui_settings['fighting_msg_width'], '0: Back', -1, -1,
                            self.colors['black'], self.colors['black'], self.fighting_panel)

        elif self.fight_state == 'choosing item':
            items = player.get_usable_items()

            x = 1
            i = 1
            for item in items:
                self.render_bar(x, 1, self.gui_settings['fighting_msg_width'] * 3,
                                f'{i}: {item.name}({item.count})', -1, -1,
                                self.colors['black'], self.colors['black'], self.fighting_panel)
                x += self.gui_settings['fighting_msg_width'] * 3 + self.gui_settings['fighting_msg_indent']
            self.render_bar(x, 1, self.gui_settings['fighting_msg_width'], '0: Back', -1, -1,
                            self.colors['black'], self.colors['black'], self.fighting_panel)

        self.root.blit(self.fighting_panel, 0, self.gui_settings['fighting_panel_y'],
                       self.gui_settings['screen_width'], self.gui_settings['fighting_panel_height'], 0, 0)

        # show the player's stats
        self.panel.clear(fg=self.colors['black'], bg=self.colors['black'])

        self.render_bar(1, 0, self.gui_settings['bar_width'], 'PLAYER', -1, -1,
                        self.colors['black'], self.colors['black'], self.panel)

        self.render_bar(1, 1, self.gui_settings['bar_width'], 'HP', player.hp, player.max_hp,
                        self.colors['hp_ft'], self.colors['hp_bg'], self.panel)

        # show the player's stats
        if self.fight_state != 'ready to quit':
            self.render_bar(self.gui_settings['screen_width'] - 1 - self.gui_settings['bar_width'],
                            0, self.gui_settings['bar_width'], chosen_monster.name, -1, -1,
                            self.colors['black'], self.colors['black'], self.panel)

            self.render_bar(self.gui_settings['screen_width'] - 1 - self.gui_settings['bar_width'],
                            1, self.gui_settings['bar_width'], 'HP', chosen_monster.current_hp,
                            chosen_monster.hp, self.colors['hp_ft'], self.colors['hp_bg'], self.panel)

        self.panel.draw_str(self.gui_settings['msg_x'], 1, "FIGHT", bg=None, fg=self.colors['red'])

        y = 2
        for (line, color) in self.fighting_msgs:
            self.panel.draw_str(self.gui_settings['msg_x'], y, line, bg=None, fg=color)
            y += 1

        self.root.blit(self.panel, 0, self.gui_settings['panel_y'], self.gui_settings['screen_width'],
                       self.gui_settings['panel_height'], 0, 0)

    @staticmethod
    def render_monsters_screen(monsters, fighting_console, chosen_monster_index, previous_arrow):

        num_of_monsters_on_screen = 2  # That's how much monster images can be on the screen and look good
        # with current settings
        arrow_y = 20  # That's how it looks best
        indention = 2  # 2 pixels indention from previous element

        left_arrow = image_load(os.path.abspath('images/arrows/left.png'))
        right_arrow = image_load(os.path.abspath('images/arrows/right.png'))

        width_of_previous_elements = 0

        if previous_arrow == 'right':
            if chosen_monster_index > 1:
                if len(monsters) - chosen_monster_index - 1 >= 2:
                    monsters_on_screen = monsters[
                                         chosen_monster_index: chosen_monster_index + num_of_monsters_on_screen]
                    chosen_monster_index_on_screen = 0
                else:
                    monsters_on_screen = monsters[
                                         chosen_monster_index - num_of_monsters_on_screen + 1: chosen_monster_index + 1]
                    chosen_monster_index_on_screen = 1
            else:
                monsters_on_screen = monsters[0: num_of_monsters_on_screen]
                chosen_monster_index_on_screen = chosen_monster_index

        else:
            if chosen_monster_index >= 1:
                if len(monsters) - chosen_monster_index >= 2:
                    monsters_on_screen = monsters[
                                         chosen_monster_index: chosen_monster_index + num_of_monsters_on_screen]
                    chosen_monster_index_on_screen = 0
                else:
                    monsters_on_screen = monsters[
                                         chosen_monster_index - num_of_monsters_on_screen + 1: chosen_monster_index + 1]
                    chosen_monster_index_on_screen = 0
            else:
                monsters_on_screen = monsters[0: num_of_monsters_on_screen]
                chosen_monster_index_on_screen = chosen_monster_index

        if chosen_monster_index > 1 or chosen_monster_index >= 1 and previous_arrow == 'left':
            left_arrow.blit_2x(fighting_console, 0, arrow_y, 0, 0, -1, -1)
        width_of_previous_elements += left_arrow.width // 2

        for i in range(len(monsters_on_screen)):
            monster = monsters_on_screen[i]
            if i == chosen_monster_index_on_screen:
                image_path = os.path.abspath(f'images/monsters/small_bordered/{monster.fighting_image}.png')
            else:
                image_path = os.path.abspath(f'images/monsters/small/{monster.fighting_image}.png')
            monster_image = image_load(image_path)
            monster_image.blit_2x(fighting_console, width_of_previous_elements + indention, 3, 0, 0, -1, -1)
            width_of_previous_elements += indention + monster_image.width // 2

        if len(monsters) > 2 and len(monsters) - chosen_monster_index > 1 and \
                not (len(monsters) - chosen_monster_index == 2 and previous_arrow == 'left'):
            right_arrow.blit_2x(fighting_console, width_of_previous_elements + indention, arrow_y, 0, 0, -1, -1)

    @staticmethod
    def clear_messages(game_msgs):
        game_msgs.clear()

    def message(self, new_msg, game_msgs, color_name='white'):
        # split the message if necessary, among multiple lines
        color = self.colors[color_name]

        new_msg_lines = textwrap.wrap(new_msg, self.gui_settings['msg_width'])
        if self.game_state == 'fighting':
            msg_height = self.gui_settings['fighting_msg_height']
        else:
            msg_height = self.gui_settings['msg_height']
        for line in new_msg_lines:
            # if the buffer is full, remove the first line to make room for the new one
            if len(game_msgs) == msg_height:
                del game_msgs[0]

            # add the new line as a tuple, with the text and the color
            game_msgs.append((line, color))

    def render_bar(self, x, y, total_width, name, value, maximum, bar_color, back_color, panel):
        # render a bar (HP, experience, etc). first calculate the width of the bar
        bar_width = int(float(value) / maximum * total_width)

        # render the background first
        panel.draw_rect(x, y, total_width, 1, None, bg=back_color)

        # now render the bar on top
        if bar_width > 0:
            panel.draw_rect(x, y, bar_width, 1, None, bg=bar_color)

        # finally, some centered text with the values
        if value != -1 and maximum != -1:
            text = name + ': ' + str(value) + '/' + str(maximum)
        else:
            text = name
        x_centered = x + (total_width - len(text)) // 2
        panel.draw_str(x_centered, y, text, fg=self.colors['white'], bg=None)

    def handle_player_action(self, player_action):
        if self.game_state == 'playing':
            # movement keys
            if player_action == 'UP':
                self.model.player_move_or_attack(0, -1, self)

            elif player_action == 'DOWN':
                self.model.player_move_or_attack(0, 1, self)

            elif player_action == 'LEFT':
                self.model.player_move_or_attack(-1, 0, self)

            elif player_action == 'RIGHT':
                self.model.player_move_or_attack(1, 0, self)

        elif self.game_state == 'fighting' and player_action != 'didnt-take-turn':
            player = self.model.get_player()
            enemy = self.model.get_enemy()

            if self.fight_state == 'won' and player_action == 'SPACE':
                self.game_state = 'won'

            elif self.fight_state == 'dead' and player_action == 'SPACE':
                self.game_state = 'dead'

            elif player_action == 'LEFT' and not self.model.fight_just_started:
                self.previous_arrow = 'left'
                if self.model.chosen_monster_index > 0:
                    self.model.chosen_monster_index -= 1
            elif player_action == 'RIGHT' and not self.model.fight_just_started:
                self.previous_arrow = 'right'
                if self.model.chosen_monster_index < len(enemy.monsters) - 1:
                    self.model.chosen_monster_index += 1

            elif self.fight_state == 'choosing action':
                if player_action == '1':
                    self.message('Choose weapon to attack with!', self.fighting_msgs)
                    self.fight_state = 'choosing weapon'
                elif player_action == '2':
                    self.message('You chose to defend!', self.fighting_msgs)
                    self.fight_state = 'defending'
                    self.message('Press SPACE to see how it turned out', self.fighting_msgs)
                elif player_action == '3':
                    self.message('Choose item to use!', self.fighting_msgs)
                    self.fight_state = 'choosing item'
                elif player_action == '4':
                    self.message('You try to run!', self.fighting_msgs)
                    self.message('Press SPACE to see how it turned out', self.fighting_msgs)
                    self.fight_state = 'running'
            elif self.fight_state == 'choosing weapon':
                weapons = player.get_weapons()

                if player_action == '0':
                    self.fight_state = 'choosing action'
                elif int(player_action) - 1 >= len(weapons):
                    self.message('No weapon with this number!', self.fighting_msgs)
                else:
                    chosen_weapon = weapons[int(player_action) - 1]
                    player.attack_enemy(enemy.monsters, self.model.chosen_monster_index, chosen_weapon,
                                        self.model.accumulated_reward, self)
            elif self.fight_state == 'defending':
                player.defend_in_fight()
                self.fight_state = 'enemy turn'
            elif self.fight_state == 'choosing item':
                items = player.get_usable_items()
                if player_action == '0':
                    self.fight_state = 'choosing action'
                elif int(player_action) - 1 >= len(items):
                    self.message('No item with this number!', self.fighting_msgs)
                else:
                    chosen_item = items[int(player_action) - 1]
                    player.use_item_in_fight(chosen_item, self)
                    self.fight_state = 'enemy turn'
            elif self.fight_state == 'running':
                player.run_from_fight(enemy.monsters, self.model.chosen_monster_index,
                                      self.model.accumulated_reward, self)
            elif self.fight_state == 'ready to quit' and player_action == 'SPACE':
                self.clear_messages(self.fighting_msgs)
                self.game_state = 'playing'

        elif self.game_state == 'fighting' and self.fight_state == 'enemy turn':
            player = self.model.get_player()
            enemy = self.model.get_enemy()
            enemy.monsters[self.model.chosen_monster_index].take_turn_in_fight(player, self)

        return self.game_state
