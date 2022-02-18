from types import MethodType


class PlayerData:

    def __init__(self, **kwargs):
        self.max_health = kwargs.get('max_health', 100)
        self.health = kwargs.get('health', self.max_health)
        self.silver_coins = kwargs.get('silver_coins', 0)
        self.gold_coins = kwargs.get('gold_coins', 0)
        self.enemies_killed = kwargs.get('enemies_killed', 0)
        self.current_level = kwargs.get('current_level', 1)
        self.abuilities = kwargs.get('abuilities')
        self.max_level = kwargs.get('max_level', 1)
        self.total_score = kwargs.get('total_score')

        # levels data
        self.levels = kwargs.get('levels', {
            1: {'health': self.max_health, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0, 'score': 0},
            2: {'health': self.max_health, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0, 'score': 0},
            3: {'health': self.max_health, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0, 'score': 0},
            4: {'health': self.max_health, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0, 'score': 0},
            5: {'health': self.max_health, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0, 'score': 0},
            6: {'health': self.max_health, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0, 'score': 0},
        })
    
    def as_dict(self):
        result_dict = {}
        for attr in dir(self):
            if not attr.startswith('_'):
                value = getattr(self, attr)
                if type(value) != MethodType:
                    result_dict[attr] = value
        return result_dict
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    @classmethod
    def load_player_data(cls):
        from tools import load_player_data
        return load_player_data()
    