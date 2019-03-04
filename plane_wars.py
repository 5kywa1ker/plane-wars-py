#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/27 17:43
# @Author  : hfb
# @Site    : 
# @File    : plane_wars.py
# @Software: PyCharm

import pygame
import random
import sys
from pygame.locals import *


class FlyingObject(object):
    """飞行物父类
    """
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def step(self):
        """移动一步"""
        pass

    def out_of_bounds(self):
        """是否出了边界"""
        return False

    def shot_by(self, bullet):
        """判断这个飞行物体是否被子弹击中了"""
        x1 = self.x
        x2 = self.x + self.width
        y1: int = self.y
        y2 = self.y + self.height

        x = bullet.x
        y = bullet.y
        return x1 < x < x2 and y1 < y < y2


class AwardMixIn(object):
    """奖励
    """
    # 奖励类型-双倍火力
    AWARD_TYPE_DOUBLE_FIRE = 0
    # 奖励类型 - 续命
    AWARD_TYPE_LIFE = 1
    # 奖励类型-三倍火力
    AWARD_TYPE_TREBLE_FIRE = 2
    # 奖励类型-四倍火力
    AWARD_TYPE_FOURFOLD_FIRE = 3

    def get_type(self):
        """
        :return: 返回奖励类型
        """
        return AwardMixIn.AWARD_TYPE_DOUBLE_FIRE


class EnemyMixIn(object):
    """敌人
    """
    def get_score(self):
        """
        :return: 返回敌机分数
        """
        return 0


class Airplane(FlyingObject, EnemyMixIn):
    """敌机"""

    image = pygame.image.load("img/airplane.png")

    def __init__(self):
        """
        :param image: 图片
        """
        image_width, image_height = Airplane.image.get_size()
        screen_width, screen_height = Game.screen_size
        x = random.randint(0, screen_width-image_width)
        y = -image_height
        super().__init__(image_width, image_height, x, y)
        # 初始化速度
        self.speed = random.randint(1, 4)

    def get_score(self):
        """返回敌机得分5分"""
        return 5

    def step(self):
        self.y += self.speed

    def out_of_bounds(self):
        return self.y > Game.screen_size[1]


class Bee(FlyingObject, AwardMixIn):
    """蜜蜂"""
    image = pygame.image.load("img/bee.png")

    def __init__(self):
        image_width, image_height = Bee.image.get_size()
        screen_width, screen_height = Game.screen_size
        x = random.randint(0, screen_width - image_width)
        y = -image_height
        super().__init__(image_width, image_height, x, y)
        self.x_speed = 1
        self.y_speed = 2
        self.award_type = random.randint(0, 3)

    def get_type(self):
        return self.award_type

    def step(self):
        self.x += self.x_speed
        self.y += self.y_speed
        if self.x >= Game.screen_size[0] - self.width:
            self.x_speed = -1
        if self.x <= 0:
            self.x_speed = 1

    def out_of_bounds(self):
        return self.y > Game.screen_size[1]


class Bullet(FlyingObject):
    """子弹"""
    image = pygame.image.load("img/bullet.png")
    image_width, image_height = image.get_size()

    def __init__(self, x, y):

        self.speed = -3
        super().__init__(Bullet.image_width, Bullet.image_height, x, y)

    def step(self):
        self.y += self.speed

    def out_of_bounds(self):
        return self.y > Game.screen_size[1]


class Hero(FlyingObject):
    """英雄机"""
    images = (pygame.image.load("img/hero0.png"), pygame.image.load("img/hero1.png"))
    image = images[0]

    def __init__(self):
        image_width, image_height = Hero.images[0].get_size()
        screen_width, screen_height = Game.screen_size
        x = (screen_width - image_width) // 2
        y = (screen_height - image_height) // 2 + 50
        super().__init__(image_width, image_height, x, y)
        self.life = 3
        self.fire = 1
        self.index = 0

    def step(self):
        self.index += 1
        Hero.image = Hero.images[self.index // 10 % 2]

    def move_to(self, x, y):
        """
        移动到某个位置
        :param x: x坐标
        :param y: y坐标
        :return: None
        """
        self.x = x - self.width//2
        self.y = y - self.height//2

    def shoot(self):
        """射击
        :return: 返回一组子弹Bullet
        """
        bullet_list = []
        bullet_space = 10
        y_off_set = self.y - 10
        if self.fire > 1:
            total_width = (self.fire * Bullet.image_width) + ((self.fire - 1) * bullet_space)
            first_bullet_x = self.x + abs((self.width - total_width) // 2)
            for i in range(self.fire):
                bullet_x = first_bullet_x + (i * (Bullet.image_width + bullet_space))
                bullet_list.append(Bullet(bullet_x, y_off_set))
        else:
            bullet_x_offset = self.x + (self.width // 2)
            bullet_list.append(Bullet(bullet_x_offset, y_off_set))
        return bullet_list

    def add_life(self):
        """加一条命"""
        self.life += 1

    def subtract_life(self):
        """减一条命"""
        self.life -= 1

    def get_life(self):
        return self.life

    def reset_fire(self):
        self.fire = 1

    def set_fire(self, fire):
        if self.fire < fire:
            self.fire = fire

    def hit(self, flying_obj):
        x1 = flying_obj.x - self.x // 2
        x2 = flying_obj.x + flying_obj.width + self.width // 2
        y1 = flying_obj.y - self.height // 2
        y2 = flying_obj.y + flying_obj.height + self.height // 2
        x = self.x + self.width // 2
        y = self.y + self.height // 2
        return x1 <= x <= x2 and y1 <= y <= y2


class Game(object):
    # 初始屏幕大小
    screen_size = (400, 654)
    # 状态-开始
    status_start = 0
    # 状态-游戏中
    status_running = 1
    # 状态-暂停
    status_pause = 2
    # 状态-结束
    status_over = 3
    # 加载图片资源
    img_background = pygame.image.load("img/background.png")
    img_start = pygame.image.load("img/start.png")
    img_pause = pygame.image.load("img/pause.png")
    img_game_over = pygame.image.load("img/gameover.png")

    def __init__(self):
        self.hero = Hero()
        self.flies = []
        self.bullets = []
        self.score = 0
        self.state = Game.status_start
        self.enter_index = 0
        self.enter_rate = 40
        self.shoot_index = 0
        self.shoot_rate = 20

    def enter_actoin(self):
        """生产飞行物 敌机和蜜蜂"""
        self.enter_index += 1
        if self.enter_index % self.enter_rate == 0:
            fly_type = random.randint(0, 20)
            if fly_type == 0:
                fly_obj = Bee()
            else:
                fly_obj = Airplane()
            self.flies.append(fly_obj)

    def step_action(self):
        """走一步"""
        self.hero.step()
        for fly_obj in self.flies:
            fly_obj.step()
        for bullet in self.bullets:
            bullet.step()

    def shoot_action(self):
        """射击"""
        self.shoot_index += 1
        if self.shoot_index % self.shoot_rate == 0:
            self.bullets.extend(self.hero.shoot())

    def out_of_bounds_action(self):
        """删除越界的飞行物"""
        if len(self.flies):
            for i, fly_obj in enumerate(self.flies):
                if fly_obj.out_of_bounds():
                    self.flies.pop(i)
        if len(self.bullets) > 0:
            for j, bullet in enumerate(self.bullets):
                if bullet.out_of_bounds():
                    self.bullets.pop(j)

    def hit_action(self):
        """子弹射击检测"""
        shot_obj = None
        for i, bullet in enumerate(self.bullets):
            for j, fly_obj in enumerate(self.flies):
                if fly_obj.shot_by(bullet):
                    shot_obj = fly_obj
                    self.flies.pop(j)
                    self.bullets.pop(i)
                    break
        if shot_obj is not None:
            if isinstance(shot_obj, EnemyMixIn):
                self.score += shot_obj.get_score()
            elif isinstance(shot_obj, AwardMixIn):
                award_type = shot_obj.get_type()
                if award_type == AwardMixIn.AWARD_TYPE_DOUBLE_FIRE:
                    self.hero.set_fire(2)
                elif award_type == AwardMixIn.AWARD_TYPE_FOURFOLD_FIRE:
                    self.hero.set_fire(4)
                elif award_type == AwardMixIn.AWARD_TYPE_TREBLE_FIRE:
                    self.hero.set_fire(3)
                elif award_type == AwardMixIn.AWARD_TYPE_LIFE:
                    self.hero.add_life()

    def check_game_over_action(self):
        """英雄机碰撞检测"""
        for i, fly_obj in enumerate(self.flies):
            if self.hero.hit(fly_obj):
                self.hero.subtract_life()
                self.hero.reset_fire()
                self.flies.pop(i)
        if self.hero.get_life() <= 0:
            self.state = self.status_over

    def game_action(self):
        """游戏流程"""
        if self.state == self.status_running:
            # 敌机/蜜蜂入场
            self.enter_actoin()
            # 飞行物走一步
            self.step_action()
            # 英雄机射击
            self.shoot_action()
            # 删除越界的飞行物
            self.out_of_bounds_action()
            # 子弹与敌人碰撞检测
            self.hit_action()
            # 英雄机与敌人碰撞检测
            self.check_game_over_action()

    def paint_action(self, window, font):
        """重绘流程"""
        # 画背景
        Game.repeat_paint_img(window, Game.img_background, Game.screen_size)
        # 画英雄机
        window.blit(Hero.image, (self.hero.x, self.hero.y))
        # 画飞行物
        for obj in self.flies:
            window.blit(obj.image, (obj.x, obj.y))
        # 画子弹
        for bullet in self.bullets:
            window.blit(Bullet.image, (bullet.x, bullet.y))
        # 画分数和生命值
        Game.paint_font(window, font, "SCORE:%d" % self.score, (10, 100, 200), 10, 25)
        Game.paint_font(window, font, "LIFE:%d" % self.hero.get_life(), (10, 100, 200), 10, 50)
        # 画游戏状态
        if self.state == self.status_start:
            Game.repeat_paint_img(window, Game.img_start, Game.screen_size)
        elif self.state == self.status_pause:
            Game.repeat_paint_img(window, Game.img_pause, Game.screen_size)
        elif self.state == self.status_over:
            Game.repeat_paint_img(window, Game.img_game_over, Game.screen_size)
        pygame.display.update()

    @staticmethod
    def paint_font(surface, font_obj, content, content_color, left, top):
        font_content = font_obj.render(content, True, content_color)
        font_content_rect = font_content.get_rect()
        font_content_rect.left = left
        font_content_rect.top = top
        surface.blit(font_content, font_content_rect)

    @staticmethod
    def repeat_paint_img(surface, img, surface_size):
        surface_width, surface_height = surface_size
        image_width, image_height = img.get_size()
        m = surface_width // image_width + 1
        n = surface_height // image_height + 1
        y = 0
        for i in range(n):
            for j in range(m):
                surface.blit(img, (j * image_width, y))
            y += image_height


if __name__ == '__main__':
    # 初始化pygame
    pygame.init()
    # 初始化窗口
    window = pygame.display.set_mode(Game.screen_size, 0, 32)
    pygame.display.set_caption("飞机大战-python")
    font = pygame.font.SysFont("arial", 20)
    # 设置刷新率30FPS
    pygame.time.Clock().tick(30)
    game = Game()
    while True:
        game.game_action()
        game.paint_action(window, font)
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                # 鼠标移动事件
                if game.state == Game.status_running:
                    game.hero.move_to(event.pos[0], event.pos[1])
            elif event.type == MOUSEBUTTONDOWN:
                # 鼠标按下
                if game.state == Game.status_running:
                    game.state = Game.status_pause
            elif event.type == VIDEORESIZE:
                # 窗口大小调整
                Game.screen_size = event.size
                window = pygame.display.set_mode(Game.screen_size, RESIZABLE, 32)
            elif event.type == KEYDOWN:
                # 键盘按下事件
                if event.key == K_SPACE:
                    if game.state == Game.status_pause or game.state == Game.status_start:
                        game.state = Game.status_running
                    elif game.state == Game.status_over:
                        game = Game()
            elif event.type == QUIT:
                pygame.quit()
                sys.exit(0)


    







