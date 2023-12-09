import pygame
from bullet import Bullet


def test_bullet_update():
    ai_game = MockAiGame() 
    bullet = Bullet(ai_game)
    bullet.update()
    assert bullet.rect.y == bullet.y


class MockAiGame:
    def __init__(self):
        self.screen = pygame.Surface((800, 600))
        self.settings = MockSettings()
        self.ship = MockShip()


class MockSettings:
    def __init__(self):
        self.bullet_color = (255, 255, 255)  
        self.bullet_width = 5  
        self.bullet_height = 10  
        self.bullet_speed = 2  


class MockShip:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 10, 10) 

    @property
    def midtop(self):
        return self.rect.midtop