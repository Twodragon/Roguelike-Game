from random import randint
from math import sqrt
from src.Monster_Factory import MonsterFactory


class Tile:
    # a tile of the map and its properties
    def __init__(self):
        self.is_initialized = False
        self.is_part_of_cluster = False
        self.is_blocked = False
        self.is_grass = False
        self.is_sand = False
        self.is_center_of_grass_cluster = False
        self.is_center_of_sand_cluster = False
        self.is_center_of_village = False
        self.is_part_of_grass_cluster = False
        self.is_part_of_sand_cluster = False
        self.is_part_of_village = False

    def set_as_grass(self, part_of_cluster=False):
        self.is_initialized = True
        self.is_grass = True
        self.is_part_of_cluster = part_of_cluster

    def set_as_sand(self, part_of_cluster=False):
        self.is_initialized = True
        self.is_sand = True
        self.is_part_of_cluster = part_of_cluster

    def set_as_center_of_grass_cluster(self):
        self.is_initialized = True
        self.is_center_of_grass_cluster = True
        self.is_grass = True
        self.is_part_of_cluster = True

    def set_as_center_of_sand_cluster(self):
        self.is_initialized = True
        self.is_center_of_sand_cluster = True
        self.is_sand = True
        self.is_part_of_cluster = True

    def set_as_center_of_village_cluster(self):
        self.is_initialized = True
        self.is_center_of_village = True
        self.is_part_of_village = True
        self.is_part_of_cluster = True

    def set_as_part_of_grass_cluster(self):
        self.is_initialized = True
        self.is_sand = True
        self.is_part_of_village = True
        self.is_part_of_cluster = True

    def set_as_part_of_village(self):
        self.is_initialized = True
        self.is_part_of_village = True
        self.is_part_of_cluster = True

    def get_type(self):
        if self.is_initialized is True:
            if self.is_grass is True:
                return 'grass'
            elif self.is_sand is True:
                return 'sand'
            else:
                return 'village'
        else:
            return 'uninitialized'


def manhattan_distance(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


class Map:
    def __init__(self, map_width, map_height, screen_width, screen_height):
        self.field = [[Tile() for _ in range(map_height)] for __ in range(map_width)]
        self.center_y = map_height / 2
        self.center_x = map_width / 2
        self.map_height = map_height
        self.map_width = map_width
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.clusters = []
        self.previous_field = None
        self.previous_left_down_corner_x = None
        self.previous_left_down_corner_y = None
        if not (map_width % 2 == 0 and map_height % 2 == 0):
            raise AttributeError("Map width and height must not be odd!")

    def at(self, x, y):
        if x + self.center_x > self.map_width:
            ans_x = (- (self.map_width - (x + self.center_x))) % self.map_width
        elif x + self.center_x < 0:
            ans_x = (self.map_width + (x + self.center_x)) % self.map_width
        else:
            ans_x = (x + self.center_x) % self.map_width

        if y + self.center_y > self.map_height:
            ans_y = (- (self.map_height - (y + self.center_y))) % self.map_height
        elif y + self.center_y < 0:
            ans_y = (self.map_height + (y + self.center_y)) % self.map_height
        else:
            ans_y = (y + self.center_y) % self.map_height

        return self.field[int(ans_x)][int(ans_y)]

    def get_k_neighbors(self, x, y, k):
        neighbors = []
        for i in range(-1, 1):
            for j in range(-1, 1):
                if i == 0 and j == 0:
                    continue
                nx = x + i
                ny = y + j
                if self.at(nx, ny).is_initialized is True:
                    neighbors.append(self.at(nx, ny))

        while len(neighbors) > k:
            neighbors.pop(randint(0, len(neighbors)))

        return neighbors

    def set_cluster(self, x, y, radius, type_of_cluster):

        if type_of_cluster == 'grass':
            self.at(x, y).set_as_center_of_grass_cluster()
            for i in range(-radius, radius):
                for j in range(-radius, radius):
                    if i == 0 and j == 0:
                        continue
                    self.at(x + i, y + j).set_as_grass(True)

        elif type_of_cluster == 'sand':
            self.at(x, y).set_as_center_of_sand_cluster()
            for i in range(-radius, radius):
                for j in range(-radius, radius):
                    if i == 0 and j == 0:
                        continue
                    self.at(x + i, y + j).set_as_sand(True)

        elif type_of_cluster == 'village':
            self.at(x, y).set_as_center_of_village_cluster()
            for i in range(-radius, radius):
                for j in range(-radius, radius):
                    if i == 0 and j == 0:
                        continue
                    self.at(x + i, y + j).set_as_part_of_village()

        self.clusters.append((x, y, radius))

    def check_distance_to_clusters(self, x, y, radius, min_distance_between_clusters):
        for cluster in self.clusters:
            if manhattan_distance((x, y), cluster[0:2]) <= min_distance_between_clusters \
                    or manhattan_distance((x, y), cluster[0:2]) <= radius + cluster[2]:
                return False
            """
            if type_of_cluster == self.at(*cluster[0:2]).get_type():  # check!
                if manhattan_distance((x, y), cluster[0:2]) <= radius:  # check!
                    return False
            else:
                if manhattan_distance((x, y), cluster[0:2]) <= radius + cluster[2]:
                    return False
            """
        return True

    def roll_type(self, x, y, grass_prob):
        if randint(0, 100) < grass_prob:
            self.at(x, y).set_as_grass()
        else:
            self.at(x, y).set_as_sand()

    def roll_type_based_on_neighbors(self, x, y, neighbors, grass_prob, sand_prob, add_prob_near_grass,
                                     add_prob_near_sand):
        new_grass_prob = grass_prob
        new_sand_prob = sand_prob
        for neighbor in neighbors:
            if neighbor.get_type() == 'grass':
                new_grass_prob += add_prob_near_grass

            elif neighbor.get_type() == 'village':
                new_grass_prob += add_prob_near_grass

            else:
                new_sand_prob += add_prob_near_sand
        normalized_grass_prob = new_grass_prob / (new_grass_prob + new_sand_prob)
        # normalized_sand_prob = new_sand_prob / (new_grass_prob + new_sand_prob)

        if randint(0, 100) < normalized_grass_prob:
            self.at(x, y).set_as_grass()
        else:
            self.at(x, y).set_as_sand()

    def get_first_visible_field(self, x, y):
        # x and y are coordinates of player, who is always in the center of the screen
        # returns visible part of the map
        self.previous_left_down_corner_x = x - self.screen_width // 2
        self.previous_left_down_corner_y = y - self.screen_height // 2

        visible_field = None
        if (self.previous_left_down_corner_x + self.screen_width < self.map_width) and \
                (self.previous_left_down_corner_y + self.screen_height < self.map_height):
            visible_field = [self.field[i][self.previous_left_down_corner_y:
                                           self.previous_left_down_corner_y + self.screen_height] for i in
                             range(self.previous_left_down_corner_x, self.previous_left_down_corner_x +
                                   self.screen_width)]
            self.previous_field = visible_field
        return visible_field

    def update_visible_field(self, dx, dy):
        visible_field = [[None for _ in range(self.screen_height)] for __ in range(self.screen_width)]

        if dx == 0 and dy == 1:
            for x in range(self.screen_width):
                for y in range(self.screen_height):
                    if y == self.screen_height - 1:
                        visible_field[x][y] = self.field[(self.previous_left_down_corner_x + x) %
                                                         self.map_width][(self.previous_left_down_corner_y +
                                                                          self.screen_height) % self.map_height]
                    else:
                        visible_field[x][y] = self.previous_field[x][y+1]

        elif dx == 0 and dy == -1:
            for x in range(self.screen_width):
                for y in range(self.screen_height):
                    if y == 0:
                        visible_field[x][y] = self.field[(self.previous_left_down_corner_x + x) %
                                                         self.map_width][(self.previous_left_down_corner_y - 1) %
                                                                         self.map_height]
                    else:
                        visible_field[x][y] = self.previous_field[x][y - 1]

        elif dx == 1 and dy == 0:
            for x in range(self.screen_width):
                for y in range(self.screen_height):
                    if x == self.screen_width - 1:
                        visible_field[x][y] = self.field[(self.previous_left_down_corner_x + self.screen_width + 1) %
                                                         self.map_width][(self.previous_left_down_corner_y + y) %
                                                                         self.map_height]
                    else:
                        visible_field[x][y] = self.previous_field[x + 1][y]

        elif dx == -1 and dy == 0:
            for x in range(self.screen_width):
                for y in range(self.screen_height):
                    if x == 0:
                        visible_field[x][y] = self.field[(self.previous_left_down_corner_x - 1) %
                                                         self.map_width][(self.previous_left_down_corner_y + y) %
                                                                         self.map_height]
                    else:
                        visible_field[x][y] = self.previous_field[x - 1][y]

        self.previous_field = visible_field
        self.previous_left_down_corner_x += dx
        self.previous_left_down_corner_y += dy
        return visible_field

    def dist_coord(self, x1, x2, type_of_coord):
        if x1 > x2:
            x1, x2 = x2, x1

        dist1 = x2 - x1
        if type_of_coord == 'x':
            dist2 = self.map_width - x2 + x1
        else:
            dist2 = self.map_height - x2 + x1

        if dist1 > dist2:
            return dist2
        else:
            return dist1

    def get_distance(self, x1, y1, x2, y2):
        return sqrt(self.dist_coord(x1, x2, 'x')**2 + self.dist_coord(y1, y2, 'y')**2)

    def is_blocked(self, x, y, objects):
        # first test the map tile
        if self.field[x][y].is_blocked:
            return True

        # now check for any blocking objects
        for obj in objects:
            if obj.blocks and obj.x == x and obj.y == y:
                return True

        return False


class MapGenerator:

    def __init__(self, map_width, map_height, screen_width, screen_height, planet_id, number_of_monster_groups):
        self.map_width = map_width
        self.map_height = map_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.number_of_monster_groups = number_of_monster_groups
        self.monster_factory = MonsterFactory.get_instance(planet_id)

    def generate_monsters(self, generated_map):
        # choose random number of monsters
        # num_monsters = randint(0, self.MAX_ROOM_MONSTERS)

        monster_groups = []
        game_objects = []

        for i in range(self.number_of_monster_groups):
            game_object, monster_group = self.monster_factory.generate_monster_group(generated_map)
            game_objects.append(game_object)
            monster_groups.append(monster_group)

        return game_objects, monster_groups

    def generate(self, parameters):
        generated_map = self.generate_first_layer_of_map(parameters)
        game_objects, monster_groups = self.generate_monsters(generated_map)
        return generated_map, game_objects, monster_groups

    def generate_first_layer_of_map(self, parameters):
        grass_prob = parameters['grass_prob']
        sand_prob = parameters['sand_prob']  # it's either grass or sand on first layer, so grass_prob + sand_prob = 1
        grass_cluster_prob = parameters['grass_cluster_prob']
        sand_cluster_prob = parameters['sand_cluster_prob']
        min_distance_between_clusters = parameters['min_distance_between_clusters']
        max_grass_cluster_radius = parameters['max_grass_cluster_radius']
        max_sand_cluster_radius = parameters['max_sand_cluster_radius']
        added_prob_near_grass = parameters['added_prob_near_grass']
        added_prob_near_sand = parameters['added_prob_near_sand']
        village_radius = parameters['village_radius']
        k_neighbors = parameters['k_neighbors']

        generated_map = Map(self.map_width, self.map_height, self.screen_width, self.screen_height)

        generated_map.set_cluster(0, 0, village_radius, 'village')  # center of map is center of the village

        # first we choose clusters

        for x in range(-self.map_width // 2, self.map_width // 2):
            for y in range(-self.map_height // 2, self.map_height // 2):
                # print(f'{x}, {y}')
                if x == 0 and y == 0:
                    continue
                # try grass cluster
                if randint(0, 100) < grass_cluster_prob:
                    radius = randint(1, max_grass_cluster_radius)
                    if generated_map.check_distance_to_clusters(x, y, radius, min_distance_between_clusters) \
                            is True:
                        generated_map.set_cluster(x, y, radius, 'grass')

                # try sand cluster
                if randint(0, 100) < sand_cluster_prob:
                    radius = randint(1, max_sand_cluster_radius)
                    if generated_map.check_distance_to_clusters(x, y, radius, min_distance_between_clusters) \
                            is True:
                        generated_map.set_cluster(x, y, radius, 'sand')

        for x in range(-self.map_width // 2, self.map_width // 2):
            for y in range(-self.map_height // 2, self.map_height // 2):
                if generated_map.at(x, y).is_initialized is True:
                    continue
                neighbors = generated_map.get_k_neighbors(x, y, k_neighbors)
                if len(neighbors) < k_neighbors:
                    generated_map.roll_type(x, y, grass_prob)
                else:
                    generated_map.roll_type_based_on_neighbors(x, y, neighbors, grass_prob, sand_prob,
                                                               added_prob_near_grass, added_prob_near_sand)

        return generated_map
