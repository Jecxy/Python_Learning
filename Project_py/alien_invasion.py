import sys
from time import sleep
import pygame

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.colock=pygame.time.Clock()
        self.settings=Settings()
        self.screen=pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.stats=GameStats(self)
        self.sb=Scoreboard(self)
        self.ship=Ship(self)
        self.bullets=pygame.sprite.Group()
        self.aliens=pygame.sprite.Group()
        self._create_fleet()

        self.game_active=False
        self.play_button=Button(self,"Play")
        pygame.display.set_caption("Alien Invasion")


    #游戏主循环
    def run_game(self):
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                
            self._update_screen()
            self.colock.tick(60)#游戏60帧


    def _check_events(self):
        #监听
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            #按下
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            
            #松开
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos=pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self,event):
        """"响应按下"""
        if event.key == pygame.K_RIGHT:
            #右移飞船
            self.ship.moving_right=True
        elif event.key == pygame.K_LEFT:
            #左移飞船
            self.ship.moving_left=True
        elif event.key == pygame.K_SPACE:
            #开火
            self._fire_bullet()
        elif event.key == pygame.K_q:
            sys.exit()

    def _check_keyup_events(self,event):
        """"响应松开"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self,mouse_pos):
        """点击Play开始新游戏"""
        button_clicked=self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            #还原游戏设置
            self.settings.initialize_dynamic_settings()
            #重置游戏的统计信息
            self.stats.reset_stats()
            self.game_active=True
            #清空外星人和子弹
            self.bullets.empty()
            self.aliens.empty()
            #创建新的外星人舰队，并将飞船放到屏幕中央底部
            self._create_fleet()
            self.ship.center_ship()
            #隐藏光标
            pygame.mouse.set_visible(False)

    def _fire_bullet(self):
        """创建一颗子弹,并将其装入编组bullets"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
        
    def _update_bullets(self):
        #更新子弹位置
        self.bullets.update()
        #删除已经消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人的碰撞"""
        #检查是否有子弹击中了外星人，击中则双方同时删除
        collsions = pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)
        if collsions:
            for aliens in collsions.values():
                self.stats.score += self.settings.alien_points*len(aliens)
            self.sb.prep_score()
        if not self.aliens:
            #删除现有的子弹并创建一个新的外星舰队
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

    def _create_fleet(self):
        """创建一个外星舰队"""
        #创建一个外星人，再不断添加，直到没有空间
        #外星人的间距为外星人的宽度和外星人的高度
        alien = Alien(self)
        alien_width,alien_height=alien.rect.size
        
        current_x,current_y=alien_width,alien_height
        while current_y<(self.settings.screen_height-5*alien_height):
            while current_x < (self.settings.screen_width-2*alien_width):
                self._create_aliens(current_x,current_y)
                current_x += 2*alien_width

            #创建一行外星人后重置x值并且传递y值
            current_x=alien_width
            current_y+=2*alien_height

    def _create_aliens(self,x_position,y_position):
            """创建一个外星人,并将其加入到舰队中"""
            new_alien=Alien(self)
            new_alien.x=x_position
            new_alien.rect.x=x_position
            new_alien.rect.y=y_position
            self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_aliens_bottum(self):
        """检查是否有外星人到达了屏幕底端"""
        screen_rect=self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #像飞船被撞击到一样处理
                self._ship_hit()
                break

    def _change_fleet_direction(self):
        """将整队外星人下移，并改变他们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y+=self.settings.fleet_drop_speed
        self.settings.fleet_direction*=-1

    def _update_aliens(self):
        """更新外星舰队中外星人的位置"""
        self.aliens.update()
        self._check_fleet_edges()
        
        #检测外星人与飞船的碰撞
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()

        #检测是否有外星人到达了屏幕底部
        self._check_aliens_bottum()

    def _ship_hit(self):
        """响应飞船被外星人撞到的响应"""
        #将ships_left减1
        if self.stats.ships_left>0:
            self.stats.ships_left-=1
            #清空外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            #创建新的外形舰队，并把飞船放在屏幕中央底部
            self._create_fleet()
            self.ship.center_ship()

            #暂停
            sleep(0.5)
        else:
            self.game_active=False
            pygame.mouse.set_visible(True)

    def _update_screen(self):
        """"更新屏幕上的图像"""
        self.screen.fill(self.settings.bg_color)#每次循环都重绘屏幕
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()#显示子弹
        self.ship.blitme()#显示飞船
        self.aliens.draw(self.screen)#显示外星人
        self.sb.show_score()#显示分数
        
        #如果游戏处于非活动状态，就绘制Play按钮
        if not self.game_active:
            self.play_button.draw_button()

        pygame.display.flip()#显示屏幕



ai=AlienInvasion()
ai.run_game()
