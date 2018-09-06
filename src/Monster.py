from random import randint


class MonsterGroup:
    def __init__(self, game_object, ai, monsters):
        self.game_object = game_object
        self.game_object.set_owner(self)
        self.ai = ai
        self.ai.set_monster_group_owner(self)

        self.monsters = monsters

    def make_a_move(self, presenter):
        self.ai.make_a_move(presenter)

    def get_monsters_names(self):
        list_of_names = []
        for monster in self.monsters:
            list_of_names.append(monster.name)

        return list_of_names


class Monster:
    def __init__(self, name, hp, defense, power, accuracy, evading, money, chance_to_attack, defense_addition,
                 inventory, fighting_image, fighting_image_chosen):
        self.name = name
        self.inventory = inventory
        self.hp = hp
        self.current_hp = hp
        self.defense = defense
        self.power = power
        self.accuracy = accuracy
        self.evading = evading
        self.added_defense = 0
        self.money = money
        self.chance_to_attack = chance_to_attack
        self.defense_addition = defense_addition
        self.fighting_image = fighting_image
        self.fighting_image_chosen = fighting_image_chosen

    def add_item_to_inventory(self, item):
        if item in self.inventory:
            item.count += 1
        else:
            self.inventory.add(item)

    def remove_item_from_inventory(self, item):
        item.count -= 1
        if item.count == 0:
            self.inventory.remove(item)

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

    def take_turn_in_fight(self, player, presenter):

        if self.added_defense > 0:
            self.added_defense -= self.defense_addition
            self.defense -= self.defense_addition  # Player's turn is over, added defense back to 0

        player_defending = False
        if player.added_defense > 0:
            player_defending = True

        if randint(0, 100) < self.chance_to_attack or player_defending:
            # chose to attack!
            weapons = self.get_weapons()
            chosen_weapon = None

            i = 0
            while chosen_weapon is None:
                weapon = weapons[i]
                probability_of_weapon = weapon.probability_of_using
                if randint(0, 100) < probability_of_weapon:
                    chosen_weapon = weapon
                if i == len(weapons) - 1:
                    i = 0

            self.attack_player(player, chosen_weapon, presenter)

        else:
            # chose to defend!
            presenter.message(f'{self.name} defends himself!', presenter.fighting_msgs)
            self.defend_in_fight(presenter)

    def attack_player(self, player, weapon, presenter):
        if randint(0, 100) < self.accuracy - player.evading:
            max_damage = self.power + weapon.power - player.defense
            damage = randint(0, max_damage)
            if damage > 0:
                message = weapon.used_message.replace('%amount%', str(damage))
                presenter.message(message, presenter.fighting_msgs)

                player.take_damage(damage, presenter)
                if presenter.fight_state != 'dead':
                    presenter.fight_state = 'choosing action'
            else:
                presenter.message(f'{self.name} hit you, but did no damage!', presenter.fighting_msgs)
                presenter.fight_state = 'choosing action'
        else:
            presenter.message(f'{self.name} missed!', presenter.fighting_msgs)
            presenter.fight_state = 'choosing action'

    def defend_in_fight(self, game):
        self.added_defense = self.defense_addition
        self.defense += self.defense_addition
        game.fight_state = 'choosing action'
