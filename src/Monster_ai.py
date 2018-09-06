from random import randint


class MonsterAi:
    def __init__(self):
        self.owner_monster_group = None

    def make_a_move(self, game):
        pass

    def set_monster_group_owner(self, owner_monster_group):
        self.owner_monster_group = owner_monster_group

    # TODO: if PeacefulAi doesnt change, make it the base class, so AggresiveAi could call super, if monster is peaceful


class PeacefulAi(MonsterAi):
    def make_a_move(self, presenter):
        monster_game_object = self.owner_monster_group.game_object
        player_game_object = presenter.model.player.game_object
        distance = presenter.model.map.get_distance(monster_game_object.x, monster_game_object.y,
                                                    player_game_object.x, player_game_object.y)
        if distance < 2:
            presenter.model.start_fight(self.owner_monster_group, presenter)

        dx = randint(-1, 1)
        dy = randint(-1, 1)

        if dx != 0 and dy != 0:
            if randint(0, 1) == 1:
                dx = 0
            else:
                dy = 0

        self.owner_monster_group.game_object.move(dx, dy, presenter.model.map)


class AggressiveAi(MonsterAi):
    def __init__(self, attack_radius):
        super().__init__()
        self.attack_radius = attack_radius

    def make_a_move(self, presenter):
        monster_game_object = self.owner_monster_group.game_object
        player_game_object = presenter.model.player.game_object
        distance = presenter.model.map.get_distance(monster_game_object.x, monster_game_object.y,
                                                    player_game_object.x, player_game_object.y)
        if distance < 2:
            presenter.model.start_fight(self.owner_monster_group, presenter)
        elif distance < self.attack_radius:
            coordinates = [0, 0]
            # We try to move towards the player, better try the quickest rout.
            while coordinates[0] == 0 and coordinates[1] == 0:
                coord = randint(0, 1)
                try_change = randint(-1, 1)
                coordinates[coord] += try_change
                new_distance = presenter.model.map.get_distance(monster_game_object.x + coordinates[0],
                                                     monster_game_object.y + coordinates[1],
                                                     player_game_object.x, player_game_object.y)
                if new_distance > distance:
                    coordinates[coord] -= try_change  # changing it back, try again

            monster_game_object.move(coordinates[0], coordinates[1], presenter.model.map)

        else:
            dx = randint(-1, 1)
            dy = randint(-1, 1)

            if dx != 0 and dy != 0:
                if randint(0, 1) == 1:
                    dx = 0
                else:
                    dy = 0

            self.owner_monster_group.game_object.move(dx, dy, presenter.model.map)
