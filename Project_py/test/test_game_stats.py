import pytest
from game_stats import GameStats
from settings import Settings

class TestGameStats:
    @pytest.fixture
    def ai_game(self):
        settings = Settings()
        return AI_Game(settings)

    def test_reset_stats(self, ai_game):
        stats = GameStats(ai_game)  
        stats.score = 100  
        stats.ships_left = 2  
        stats.reset_stats()  
        assert stats.score == 0  
        assert stats.ships_left == ai_game.settings.ship_limit  
        assert stats.high_score == 0 
        assert stats.level == 1 

class AI_Game:
    def __init__(self, settings):
        self.settings = settings

class Settings:
    def __init__(self):
        self.ship_limit = 3