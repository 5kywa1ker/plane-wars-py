#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/27 17:43
# @Author  : hfb
# @Site    : 
# @File    : plane_wars.py
# @Software: PyCharm

import pygame, random, sys, time
from pygame.locals import *


class FlyingObject(object):
    """飞行物父类
    """
    def __init__(self, width, height, x, y):
        self.__width = width
        self.__height = height
        self.__x = x
        self.__y = y

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height

    def step(self):
        """移动一步"""
        pass

    def out_of_bounds(self):
        """是否出了边界"""
        return False

    def shot_by(self, bullet):
        """判断这个飞行物体是否被子弹击中了"""
        x1 = self.__x
        x2 = self.__x + self.__width
        y1: int = self.__y
        y2 = self.__y + self.__height

        x = bullet.get_x()
        y = bullet.get_y()
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

    image = None

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
        self.__speed = random.randint(1, 4)

    def get_score(self):
        """返回敌机得分5分"""
        return 5

    def step(self):
        self.__y += self.__speed

    def out_of_bounds(self):
        return self.__y > Game.screen_size[1]


class Bee(FlyingObject, AwardMixIn):
    """蜜蜂"""
    image = None

    def __init__(self):
        image_width, image_height = Bee.image.get_size()
        screen_width, screen_height = Game.screen_size
        x = random.randint(0, screen_width - image_width)
        y = -image_height
        super().__init__(image_width, image_height, x, y)
        self.__x_speed = 1
        self.__y_speed = 2
        self.__award_type = random.randint(0, 3)

    def get_type(self):
        return self.__award_type

    def step(self):
        self.__x += self.__x_speed
        self.__y += self.__y_speed
        if self.__x >= Game.screen_size[0] - self.__width:
            self.__x_speed = -1
        if self.__x <= 0:
            self.__x_speed = 1

    def out_of_bounds(self):
        return self.__y > Game.screen_size[1]


class Bullet(FlyingObject):
    """子弹"""
    image = None

    def __init__(self, x, y):
        image_width, image_height = Bullet.image.get_size()
        self.__speed = 3
        super().__init__(image_width, image_height, x, y)

    def step(self):
        self.__y += self.__speed

    def out_of_bounds(self):
        return self.__y > Game.screen_size[1]


class Hero(FlyingObject):
    """英雄机"""
    images = None
    image = None

    def __init__(self):
        image_width, image_height = Hero.images[0].get_size()
        screen_width, screen_height = Game.screen_size
        x = (screen_width - image_width) / 2
        y = (screen_height - image_height) / 2 + 50
        super().__init__(Hero.images[0], image_width, image_height, x, y)
        self.__life = 3
        self.__fire = 1
        self.__index = 0

    def step(self):
        self.__index += 1
        Hero.image = Hero.images[self.__index / 10 % 2]

    def move_to(self, x, y):
        """
        移动到某个位置
        :param x: x坐标
        :param y: y坐标
        :return: None
        """
        self.__x = x - self.__width/2
        self.__y = y - self.__height/2

    def shoot(self):
        """射击
        :return: 返回一组子弹Bullet
        """
        bullet_list = []
        bullet_space = 10
        y_off_set = self.__y - 10
        if self.__fire > 1:
            total_width = (self.__fire * Bullet.image.get_size[0]) + ((self.__fire - 1) * bullet_space)
            first_bullet_x = self.__x + abs((self.__width - total_width) / 2)
            for i in range(self.__fire):
                bullet_x = first_bullet_x + (i * (Bullet.image.get_size[0] + bullet_space))
                bullet_list.append(Bullet(bullet_x, y_off_set))
        else:
            bullet_x_offset = self.__x + (self.__width / 2)
            bullet_list.append(Bullet(bullet_x_offset, y_off_set))

    def add_life(self):
        """加一条命"""
        self.__life += 1

    def subtract_life(self):
        """减一条命"""
        self.__life -= 1

    def get_life(self):
        return self.__life

    def reset_fire(self):
        self.__fire = 1

    def set_fire(self, fire):
        if self.__fire < fire:
            self.__fire = fire

    def hit(self, flying_obj):
        x1 = flying_obj.get_x() - self.__x / 2
        x2 = flying_obj.get_x() + flying_obj.get_width() + self.__width / 2
        y1 = flying_obj.get_y() - self.__height / 2
        y2 = flying_obj.get_y() + flying_obj.get_height() + self.__height / 2
        x = self.__x + self.__width / 2
        y = self.__y + self.__height / 2
        return x1 <= x <= x2 and y1 <= y <= y2


class Game(object):
    # 初始屏幕大小
    screen_size = (416, 692)
    # 状态-开始
    status_start = 0
    # 状态-游戏中
    status_running = 1
    # 状态-暂停
    status_pause = 2
    # 状态-结束
    status_over = 3

    def __init__(self):
        self.hero = Hero()
        self.flies = []
        self.bullets = []
        self.score = 0
        self.state = Game.status_start

    def game_action(self):
        """游戏流程"""
        pass

    def paint_action(self, window, font):
        """重绘流程"""
        # 画背景
        window.blit(img_background, (0, 0))
        # 画英雄机
        window.blit(Hero.image, (self.hero.get_x(), self.hero.get_y()))
        # 画飞行物
        for obj in self.flies:
            window.blit(obj.image, (obj.get_x(), obj.get_y()))
        # 画子弹
        for bullet in self.bullets:
            window.blit(Bullet.image, bullet.get_x(), bullet.get_y())
        # 画分数和生命值
        score_content = font.render("SCORE:s%d" % self.score, True, (10, 100, 200))
        score_content_rect = score_content.get_rect()
        score_content_rect.left = 10
        score_content_rect.top = 25
        life_content = font.render("LIFE:s%d" % self.hero.get_life(), True, (10, 100, 200))
        life_content_rect = life_content.get_rect()
        life_content_rect.left = 10
        life_content_rect.top = 45
        window.blit(score_content, score_content_rect)
        window.blit(life_content, life_content_rect)
        # 画游戏状态

        pass


if __name__ == '__main__':
    # 初始化pygame
    pygame.init()
    # 加载图片资源
    Airplane.image = pygame.image.load("img/airplane.png")
    Bee.image = pygame.image.load("img/bee.png")
    Bullet.image = pygame.image.load("img/bullet.png")
    Hero.images = (pygame.image.load("img/hero0.png"), pygame.image.load("img/hero1.png"))
    img_background = pygame.image.load("img/background.png")
    img_start = pygame.image.load("img/start.png")
    img_pause = pygame.image.load("img/pause.png")
    img_game_over = pygame.image.load("img/gameover.png")
    # 初始化窗口
    window = pygame.display.set_mode(Game.screen_size, 0, 32)
    pygame.display.set_caption("飞机大战")
    font = pygame.font.SysFont("arial", 24)
    pygame.time.Clock().tick(30)
    window.blit(img_background, (0, 0))
    pygame.display.update()
    # while True:
    #     pygame.display.update()







