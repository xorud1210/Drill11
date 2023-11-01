# 이것은 각 상태들을 객체로 구현한 것임.
import random

from pico2d import get_time, load_image, load_font, clamp,  SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT
from ball import Ball, BigBall
import game_world
import game_framework

# state event check
# ( state event type, event value )

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def time_out(e):
    return e[0] == 'TIME_OUT'

# time_out = lambda e : e[0] == 'TIME_OUT'


# bird Run Speed
# fill here
PIXEL_PER_METER = (10.0/0.3)
RUN_SPEED_KMPH = 20.0 # 20km/h
RUN_SPEED_MPM = RUN_SPEED_KMPH * 1000.0 / 60.0
RUN_SPEED_MPS = RUN_SPEED_MPM / 60.0
RUN_SPEED_PPS = RUN_SPEED_MPS * PIXEL_PER_METER


# bird Action Speed
# fill here
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 14

FRAMES_PER_TIME = ACTION_PER_TIME * FRAMES_PER_ACTION




class Run:

    @staticmethod
    def enter(bird, e):
        if right_down(e) or left_up(e): # 오른쪽으로 RUN
            bird.dir, bird.action, bird.face_dir = 1, 1, 1
        elif left_down(e) or right_up(e): # 왼쪽으로 RUN
            bird.dir, bird.action, bird.face_dir = -1, 0, -1

    @staticmethod
    def exit(bird, e):
        if space_down(e):
            bird.fire_ball()

        pass

    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + FRAMES_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        bird.x += bird.dir * RUN_SPEED_PPS * game_framework.frame_time
        bird.x = clamp(25, bird.x, 1600-25)
        if bird.x > 1550:
            bird.dir *= -1
        elif bird.x < 50:
            bird.dir *= -1


    @staticmethod
    def draw(bird):
        if bird.dir == -1:
            bird.image.clip_composite_draw(int(bird.frame) % 5 * 183, (14 - int(bird.frame)) // 5 * 168, 180, 168,
                                          0, 'h', bird.x, bird.y, 183, 168)
        else:
            bird.image.clip_composite_draw(int(bird.frame) % 5 * 183, (14 - int(bird.frame)) // 5 * 168, 180, 168,
                                          0, '', bird.x, bird.y, 183, 168)


class StateMachine:
    def __init__(self, bird):
        self.bird = bird
        self.cur_state = Run
        self.transitions = {
            Run: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Run},
        }

    def start(self):
        self.cur_state.enter(self.bird, ('NONE', 0))

    def update(self):
        self.cur_state.do(self.bird)

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.bird, e)
                self.cur_state = next_state
                self.cur_state.enter(self.bird, e)
                return True

        return False

    def draw(self):
        self.cur_state.draw(self.bird)





class Bird:
    image = None
    def __init__(self):
        self.x, self.y = random.randint(50, 1550), random.randint(200, 550)
        self.frame = 0
        self.action = 3
        self.face_dir = 1
        self.dir = random.randint(0, 1)
        if self.dir == 0:
            self.dir = -1
        if Bird.image == None:
            Bird.image = load_image('bird_animation.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()
        self.item = 'Ball'

    def fire_ball(self):

        if self.item ==   'Ball':
            ball = Ball(self.x, self.y, self.face_dir*10)
            game_world.add_object(ball)
        elif self.item == 'BigBall':
            ball = BigBall(self.x, self.y, self.face_dir*10)
            game_world.add_object(ball)
        # if self.face_dir == -1:
        #     print('FIRE BALL LEFT')
        #
        # elif self.face_dir == 1:
        #     print('FIRE BALL RIGHT')

        pass

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
