class PlayerStats:

    def __init__(self):
        self.health = 100
        self.max_health = 100
        self.silver_coins = 0
        self.gold_coins = 0
        self.enemies_killed = 0
        self.current_level = 1
        self.max_level = 1
    
    def as_dict(self):
        return {
            'health': self.health,
            'max_health': self.max_health,
            'silver_coins': self.silver_coins,
            'gold_coins': self.gold_coins,
            'enemies_killed': self.enemies_killed,
            'current_level': self.current_level,
            'max_level': self.max_level,
        }
    
    @classmethod
    def load_player_stats(cls):
        from tools import load_player_stats
        return load_player_stats()
    
    @classmethod
    def from_dict(cls, dict_stats):
        stats = cls()
        stats.health = dict_stats['health']
        stats.max_health = dict_stats['max_health']
        stats.silver_coins = dict_stats['silver_coins']
        stats.gold_coins = dict_stats['gold_coins']
        stats.enemies_killed = dict_stats['enemies_killed']
        stats.current_level = dict_stats['current_level']
        stats.max_level = dict_stats['max_level']
        return stats
