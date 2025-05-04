class Inventory:
    def __init__(self, id: int, character_id: int, capacity: int, weight_limit: float, current_weight: float = 0.0):
        self.id = id
        self.character_id = character_id
        self.capacity = capacity
        self.weight_limit = weight_limit
        self.current_weight = current_weight
