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
    screen_size = (416, 692)
    status_start = 0
    status_running = 1
    status_pause = 2
    status_over = 3







