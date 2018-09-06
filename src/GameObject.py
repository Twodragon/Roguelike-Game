import math

class GameObject:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen.
    def __init__(self, x, y, char, color, type, name='monster', blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.type = type
        self.blocks = blocks
        self.owner = None

    def move(self, dx, dy, map):
        # move by the given amount, if the destination is not blocked
        if not map.field[(self.x + dx) % map.map_width][(self.y + dy) % map.map_height].is_blocked:
            self.x = (self.x + dx) % map.map_width
            self.y = (self.y + dy) % map.map_height

    def draw(self, con, player_x, player_y, map):
        # draw the character that represents this object at its position
        left_down_corner_x = player_x - map.screen_width // 2
        left_down_corner_y = player_y - map.screen_height // 2
        con.draw_char((self.x - left_down_corner_x) % map.map_width, (self.y - left_down_corner_y) % map.map_height, self.char, self.color, bg=None)

    def clear(self, con):
        # erase the character that represents this object
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)

    def send_to_back(self, objects):
        # make this object be drawn first, so all others appear above it if they're in the same tile.
        objects.remove(self)
        objects.insert(0, self)

    def set_owner(self, owner):
        self.owner = owner

    def get_owner(self):
        return self.owner

    def set_xy(self, x, y):
        self.x = x
        self.y = y
