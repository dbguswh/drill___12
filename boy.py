from math import pi
from pathlib import Path

import pico2d
from pico2d import get_canvas_height, get_canvas_width, get_time, load_font, load_image
from sdl2 import (SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT,
                  SDLK_SPACE)
from transitions import Machine

import game_world
from ball import Ball


class Boy:
    def __init__(self):
        self.x, self.y = 400, 30
        self.frame = 0
        self.image = load_image('animation_sheet.png')
        font_path = Path(pico2d.__file__).parent / 'data' / 'ConsolaMalgun.ttf'
        self.font = load_font(str(font_path), 20)
        self.idle_started_at = get_time()
        self.dir = 0
        self.face_dir = 1
        self.pressed_keys = set()
        self.shot_message = None
        self.shot_message_until = 0

        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN'],
            transitions=[
                {'trigger': 'fall_asleep',
                 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'wake_up',
                 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'start_run',
                 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {'trigger': 'stop_run',
                 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'fire_ball',
                 'source': ['IDLE', 'RUN'], 'dest': None,
                 'after': 'shoot_ball'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )

    def on_enter_IDLE(self):
        self.idle_started_at = get_time()
        self.frame = 0

    def on_enter_SLEEP(self):
        self.frame = 0
        self.shot_message = None

    def on_enter_RUN(self):
        self.frame = 0

    def shoot_ball(self):
        game_world.add_object(
            Ball(self.x + self.face_dir * 55, self.y, self.face_dir)
        )
        direction = '오른쪽' if self.face_dir == 1 else '왼쪽'
        self.shot_message = f'{direction}으로 볼을 발사합니다!'
        self.shot_message_until = get_time() + 1.5
        if self.state == 'IDLE':
            self.idle_started_at = get_time()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            if self.state == 'SLEEP':
                self.wake_up()
            elif self.state in ('IDLE', 'RUN'):
                self.fire_ball()
            return

        if (event.type not in (SDL_KEYDOWN, SDL_KEYUP) or
                event.key not in (SDLK_LEFT, SDLK_RIGHT)):
            return

        if event.type == SDL_KEYDOWN:
            self.pressed_keys.add(event.key)
        else:
            self.pressed_keys.discard(event.key)

        direction = (int(SDLK_RIGHT in self.pressed_keys) -
                     int(SDLK_LEFT in self.pressed_keys))

        if direction != 0:
            self.dir = direction
            self.face_dir = direction
            if self.state in ('IDLE', 'SLEEP'):
                self.start_run()
        elif self.state == 'RUN':
            self.dir = 0
            self.stop_run()

    def update(self):
        if self.state == 'IDLE':
            if get_time() - self.idle_started_at >= 5.0:
                self.fall_asleep()
            else:
                self.frame = (self.frame + 1) % 8
        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 8
            self.x += self.dir * 5
            self.x = max(25, min(get_canvas_width() - 25, self.x))

    def draw(self):
        if self.state == 'SLEEP':
            angle = pi / 2 if self.face_dir == 1 else -pi / 2
            flip = '' if self.face_dir == 1 else 'h'
            self.image.clip_composite_draw(
                self.frame * 100, 300, 100, 100,
                angle, flip, self.x, self.y - 30, 100, 100
            )
        elif self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(self.frame * 100, row, 100, 100,
                                 self.x, self.y)
        else:
            row = 300 if self.face_dir == 1 else 200
            self.image.clip_draw(self.frame * 100, row, 100, 100,
                                 self.x, self.y)

        if self.shot_message and get_time() < self.shot_message_until:
            self.font.draw(20, get_canvas_height() - 30,
                           self.shot_message, (0, 0, 0))
