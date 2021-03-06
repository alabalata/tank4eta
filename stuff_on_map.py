#!/usr/bin/env python
#-*- coding: utf8 -*-

import random

from objects import *
from pygame.locals import *
from locals import *
from utils import *


class BasicTank(MovableObject):

    image = ""
    max_bullets = 1

    def __init__(self, position, game_map):
        MovableObject.__init__(self, self.image, position, game_map)
        self.move(DIRECTION_DOWN)
        self.stop()
        self.bullets = []

    def fire(self):
        if len(self.bullets) >= self.max_bullets:
            return
        bullet = Bullet(self)
        self.bullets.append(bullet)

    def process_events(self, events):
        pass

    def _move_left(self):
        self.change_axis(AXIS_X)
        self.move(DIRECTION_LEFT)

    def _move_right(self):
        self.change_axis(AXIS_X)
        self.move(DIRECTION_RIGHT)

    def _move_up(self):
        self.change_axis(AXIS_Y)
        self.move(DIRECTION_UP)

    def _move_down(self):
        self.change_axis(AXIS_Y)
        self.move(DIRECTION_DOWN)

    def _stop(self):
        self.stop()

    def _fire(self):
        self.fire()


class EnemyTank(BasicTank):

    max_bullets = 1

    def __init__(self, position, game_map):
        num = random.randint(1, 2)
        self.image = texture_path("enemy-%d.png" % num)
        MovableObject.__init__(self, self.image, position, game_map)
        self.explosion_sound = pygame.mixer.Sound(sound_path('explosion_enemy.wav'))
        self.move(DIRECTION_DOWN)
        self.stop()
        self.bullets = []

    def explode_sound(self):
        self.explosion_sound.play()

    def process_events(self, events):
        print "EnemyTank processing event. If you see me do something."


_player_tank_number = 0


class Tank(BasicTank):

    max_bullets = 2

    def __init__(self, position, game_map):
        global _player_tank_number
        num = (_player_tank_number % 2) + 1
        _player_tank_number += 1

        sounds = {
            1: 'didi_engine_01.wav',
            2: 'doycho.wav',
        }

        textures = {
            1: 'tank.png',
            2: 'tank-of-love.png',
        }

        texture_image = textures[num]
        self.image = texture_path(texture_image)
        MovableObject.__init__(self, self.image, position, game_map)
        self.engine_working = False
        self.engine = pygame.mixer.Sound(sound_path(sounds[num]))
        self.explosion_sound = pygame.mixer.Sound(sound_path('player_death.wav'))
        self.move(DIRECTION_UP)
        self.stop()
        self.bullets = []
        self.event_map = {
            EVENT_FIRE: self._fire,
            EVENT_MOVE_LEFT: self._move_left,
            EVENT_MOVE_RIGHT: self._move_right,
            EVENT_MOVE_UP: self._move_up,
            EVENT_MOVE_DOWN: self._move_down,
            EVENT_STOP: self._stop,
        }

    def explode_sound(self):
        self.explosion_sound.play()

    def process_events(self, events):
        for event in events:
            self.event_map[event]()

    def stop(self):
        MovableObject.stop(self)
        self.engine.stop()
        self.engine_working = False

    def update(self, delta=None):
        if self.direction != DIRECTION_NONE and not self.engine_working:
            self.engine.play(loops=-1)
            self.engine_working = True

        MovableObject.update(self, delta)


class Bullet(MovableObject):

    bullet_img = texture_path('bullet.png')

    def __init__(self, owner):
        self.owner = owner
        MovableObject.__init__(self, self.bullet_img, owner.rect.center, owner.map)
        self.set_movement_speed(BULLET_SPEED)
        self.direction = owner.facing
        self.move(self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = owner.rect.center
        self.position_front_of_owner()
        self.fire_sound = pygame.mixer.Sound(sound_path('didi_gunfire_01.wav'))
        self.explosion_sound = pygame.mixer.Sound(sound_path('didi_explode_01.wav'))
        self.fire_sound.play(loops=0, maxtime=0, fade_ms=0)

    def position_front_of_owner(self):
        dx, dy = self.owner.movements[self.owner.facing]
        if dx:
            dx = dx / abs(dx)
            diff = self.owner.rect.width / 2 + self.rect.width / 2 + 1
        if dy:
            dy = dy / abs(dy)
            diff = self.owner.rect.height / 2 + self.rect.height / 2 + 1

        rx, ry = self.rect.center
        self.rect.center = (rx + diff * dx, ry + diff * dy)

    def explode_sound(self):
        self.explosion_sound.play()

    # a bullet does not stop!
    def stop(self):
        pass

    # a bullet does not care for your "events" !
    def process_event(self, event):
        pass

    def update(self, delta=None, collisions=[]):
        if self in collisions:
            self.owner.bullets.remove(self)
        x, y = self.rect.center
        dx, dy = self.movements[self.direction]
        self.rect.center = (x + dx, y + dy)


class Wall (NonMovableObject):
    image = pygame.image.load(texture_path('wall.png'))

    def __init__(self, position):
        NonMovableObject.__init__(self, position)


class Water (NonMovableObject):
    image = pygame.image.load(texture_path('water.png'))

    def __init__(self, position):
        NonMovableObject.__init__(self, position)
