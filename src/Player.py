from random import randint
import math


class Player:
    def __init__(self, game_object, hp, defense, power, accuracy, evading, xp,
                 hp_lvl_mul, defense_lvl_add, power_lvl_add, accuracy_lvl_mul, evading_lvl_mul, xp_lvl_mul,
                 added_defense):
        self.game_object = game_object
        self.xp = 0
        self.max_xp = xp
        self.inventory = set()
        self.money = 0
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.accuracy = accuracy
        self.evading = evading
        self.hp_lvl_mul = hp_lvl_mul
        self.defense_lvl_add = defense_lvl_add
        self.power_lvl_add = power_lvl_add
        self.accuracy_lvl_mul = accuracy_lvl_mul
        self.evading_lvl_mul = evading_lvl_mul
        self.xp_lvl_mul = xp_lvl_mul
        self.current_added_defense = 0
        self.added_defense = added_defense

    @staticmethod
    def player_death(presenter):
        presenter.fight_state = 'dead'
        presenter.message(f'You lost!', presenter.fighting_msgs, 'red')
        presenter.message(f'Press SPACE to quit', presenter.fighting_msgs)

    def add_item_to_inventory(self, item):
        is_in_inventory = False
        for inventory_item in self.inventory:
            if item.name == inventory_item.name:
                inventory_item.count += 1
                is_in_inventory = True
                break
        if is_in_inventory is False:
            self.inventory.add(item)

    def remove_item_from_inventory(self, item):
        for inventory_item in self.inventory:
            if item.name == inventory_item.name:
                inventory_item.count -= 1
                if item.count == 0:
                    self.inventory.remove(item)
                break

    def get_weapons(self):
        weapons = []
        for item in self.inventory:
            if item.type == 'weapon':
                weapons.append(item)
        return weapons

    def get_usable_items(self):
        items = []
        for item in self.inventory:
            if item.type == 'usable':
                items.append(item)
        return items

    def gain_xp(self, xp):
        self.xp += xp
        if self.xp >= self.max_xp:
            difference = self.xp - self.max_xp
            self.level_up(difference)
            return True
        return False

    def gain_money(self, money, presenter):
        self.money += money
        if self.money >= presenter.planet_parameters["money_to_travel_to_next_planet"]:
            self.money -= presenter.planet_parameters["money_to_travel_to_next_planet"]
            if presenter.planet_id < len(presenter.planets):
                self.travel_to_new_planet(presenter)
            else:
                presenter.fight_state = 'won'
                return 2

            return 1
        return 0

    @staticmethod
    def travel_to_new_planet(presenter):
        presenter.planet_id += 1
        presenter.model.planet_id += 1
        presenter.load_new_planet()
        presenter.model.load_new_planet()

    def level_up(self, difference):
        self.max_hp = math.floor(self.max_hp * (100 + self.hp_lvl_mul)/100.0)
        self.hp = self.max_hp
        self.defense += self.defense_lvl_add
        self.power += self.power_lvl_add
        self.accuracy = math.floor(self.accuracy * (100 + self.accuracy_lvl_mul)/100.0)
        self.evading = math.floor(self.evading_lvl_mul * (100 + self.evading_lvl_mul)/100.0)
        self.max_xp = math.floor(self.max_xp * (100 + self.xp_lvl_mul)/100.0)
        self.xp = difference

    @staticmethod
    def get_reward_for_killing_enemy(enemy, accumulated_reward, presenter):
        gained_xp = 1
        gained_money = enemy.money
        gained_inventory = enemy.inventory

        presenter.message(f'You killed {enemy.name}!', presenter.fighting_msgs)

        accumulated_reward['xp'] += gained_xp
        accumulated_reward['money'] += gained_money
        for item in gained_inventory:
            if item.type == 'usable':
                accumulated_reward['inventory'].append(item)

    def get_final_reward(self, accumulated_reward, result, presenter):
        leveled_up = self.gain_xp(accumulated_reward['xp'])
        finished_planet_code = self.gain_money(accumulated_reward['money'], presenter)
        for item in accumulated_reward['inventory']:
            if item.type == 'usable':
                self.add_item_to_inventory(item)

        if leveled_up is True:
            result += ' and leveled up!'

        presenter.message(f'You {result}!!', presenter.fighting_msgs)
        presenter.message(f'You gained {accumulated_reward["xp"]} xp!', presenter.fighting_msgs)
        presenter.message(f'You gained {accumulated_reward["money"]} gold!', presenter.fighting_msgs)
        presenter.message(f'You gained {len(accumulated_reward["inventory"])} new items!', presenter.fighting_msgs)
        if finished_planet_code == 1:
            presenter.message('You gained enough gold to travel to new planet!', presenter.fighting_msgs, 'red')
        elif finished_planet_code == 2:
            presenter.message(f'No other planets left! You won! Congratulations!', presenter.fighting_msgs, 'red')

        presenter.message(f'Press SPACE to continue', presenter.fighting_msgs)

        return finished_planet_code

    def use_item(self, item):
        characteristic_difference = 0
        if item.usage_target == 'hp':
            difference = self.max_hp - self.hp
            if difference > item.power:
                self.hp += item.power
                characteristic_difference = item.power
            else:
                self.hp = self.max_hp
                characteristic_difference = difference

        self.remove_item_from_inventory(item)
        return characteristic_difference

    def take_damage(self, damage, presenter):
        # apply damage if possible
        if damage > 0:
            self.hp -= damage
            if self.hp <= 0:
                self.player_death(presenter)

    def attack_enemy(self, monster_group, chosen_monster_index, weapon, accumulated_reward, presenter):
        if self.current_added_defense > 0:
            self.current_added_defense = 0
            self.defense -= self.added_defense
        chosen_monster = monster_group[chosen_monster_index]

        if randint(0, 100) < self.accuracy - chosen_monster.evading:
            max_damage = self.power + weapon.power - chosen_monster.defense
            damage = randint(0, max_damage)
            if damage > 0:
                message = weapon.used_message.replace('%name%', chosen_monster.name).replace('%amount%', str(damage))
                presenter.message(message, presenter.fighting_msgs)

                chosen_monster.current_hp -= damage
                if chosen_monster.current_hp <= 0:

                    self.get_reward_for_killing_enemy(chosen_monster, accumulated_reward, presenter)
                    monster_group.pop(chosen_monster_index)
                    if len(monster_group) == 0:
                        finished_planet = self.get_final_reward(accumulated_reward, 'won', presenter)
                        if finished_planet == 0:
                            presenter.model.monster_groups.remove(presenter.model.enemy)
                            presenter.model.objects.remove(presenter.model.enemy.game_object)
                            presenter.model.monster_factory.generate_monster_group(presenter.model.map)
                        if presenter.fight_state != 'won':
                            presenter.fight_state = 'ready to quit'
                else:
                    presenter.fight_state = 'enemy turn'
            else:
                presenter.message(f'You hit {chosen_monster.name}, but did no damage!', presenter.fighting_msgs)
                presenter.fight_state = 'enemy turn'
        else:
            presenter.message('You missed!', presenter.fighting_msgs)
            presenter.fight_state = 'enemy turn'

    def defend_in_fight(self):
        self.current_added_defense = self.added_defense
        self.defense += self.added_defense

    def use_item_in_fight(self, item, presenter):
        characteristic_difference = self.use_item(item)

        message = item.used_message.replace('%amount%', str(characteristic_difference))
        presenter.message(message, presenter.fighting_msgs)

    def run_from_fight(self, monster_group, chosen_monster_index, accumulated_reward, presenter):
        if randint(0, 100) < monster_group[chosen_monster_index].accuracy - self.evading:
            presenter.message('You tried to run and failed!', presenter.fighting_msgs)
            presenter.fight_state = 'enemy turn'
        else:
            finished_planet_code = self.get_final_reward(accumulated_reward, 'fled', presenter)
            if finished_planet_code == 0:
                presenter.model.monster_groups.remove(presenter.model.enemy)
                presenter.model.objects.remove(presenter.model.enemy.game_object)
                presenter.model.monster_factory.generate_monster_group(presenter.model.map)
            if presenter.fight_state != 'won':
                presenter.fight_state = 'ready to quit'
