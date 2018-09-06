class Item:
    def __init__(self, name, cost, power, use_message, used_message, item_type, probability_of_using=100,
                 usage_target=None):
        self.name = name
        self.cost = cost
        self.power = power
        self.use_message = use_message
        self.used_message = used_message
        self.type = item_type
        self.probability_of_using = probability_of_using
        self.usage_target = usage_target
        self.count = 1
