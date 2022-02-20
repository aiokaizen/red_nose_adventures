from types import MethodType


class PlayerData:

    def __init__(self, **kwargs):
        self.max_health = kwargs.get('max_health', 100)
        self.current_level = kwargs.get('current_level', 1)
        self.abuilities = kwargs.get('abuilities', [])
        self.max_level = kwargs.get('max_level', 1)
        self.preferences = kwargs.get('preferences', {
            'music_volume': 0.4,
            'vfx_volume': 0.4
        })

        # levels data
        self.levels = kwargs.get('levels', {
            1: {'score': 0, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0},
            2: {'score': 0, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0},
            3: {'score': 0, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0},
            4: {'score': 0, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0},
            5: {'score': 0, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0},
            6: {'score': 0, 'silver_coins': 0, 'gold_coins': 0, 'enemies_killed': 0},
        })
    
    def as_dict(self):
        result_dict = {}
        for attr in dir(self):
            if not attr.startswith('_'):
                value = getattr(self, attr)
                if type(value) != MethodType:
                    result_dict[attr] = value
        return result_dict
    
    def update_level_data(self, level, data, initial_state):
        if self.levels[level]['gold_coins'] < data['gold_coins']:
            self.levels[level]['gold_coins'] = data['gold_coins']
        if self.levels[level]['silver_coins'] < data['silver_coins']:
            self.levels[level]['silver_coins'] = data['silver_coins']
        if self.levels[level]['enemies_killed'] < data['enemies_killed']:
            self.levels[level]['enemies_killed'] = data['enemies_killed']

        for key, val in data.items():
            self.levels[level][f'current_{key}'] = val

        self.calculate_score(level, initial_state)
    
    def calculate_score(self, level, initial_state):
        level_state = self.levels[level]
        gold_coins_score = level_state['gold_coins'] * 100 / initial_state['gold_coins']
        silver_coins_score = level_state['silver_coins'] * 100 / initial_state['silver_coins']
        enemies_killed_score = level_state['enemies_killed'] * 100 / initial_state['enemies']

        current_gold_coins_score = level_state['current_gold_coins'] * 100 / initial_state['gold_coins']
        current_silver_coins_score = level_state['current_silver_coins'] * 100 / initial_state['silver_coins']
        current_enemies_killed_score = level_state['current_enemies_killed'] * 100 / initial_state['enemies']

        level_state['max_gold_coins'] = initial_state['gold_coins']
        level_state['max_silver_coins'] = initial_state['silver_coins']
        level_state['max_enemies'] = initial_state['enemies']

        level_state['score'] = int(sum([
            gold_coins_score * 3,
            enemies_killed_score * 2,
            silver_coins_score
        ]))
        level_state['current_score'] = int(sum([
            current_gold_coins_score * 3,
            current_enemies_killed_score * 2,
            current_silver_coins_score
        ]))
    
    def get_score(self):
        score = 0
        for level in self.levels.values():
            score += level['score']
        return score
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    @classmethod
    def load_player_data(cls):
        from tools import load_player_data
        return load_player_data()
    