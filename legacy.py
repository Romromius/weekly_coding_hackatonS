import os
import random
import json
import winsound

import pygame

COLORS = {'q': 'cyan', 'w': 'green', 'e': 'red', 'r': 'yellow',
          'й': 'cyan', 'ц': 'green', 'у': 'red', 'к': 'yellow'}
GRAVITY = 9.8
LEVEL = 'Bobepoo'


class Background(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.target = 0


def load_level(level):
    global music, voices, notes, params, background, player
    pl = False

    music = pygame.mixer.Sound(f'levels/{level}/{level}_music.ogg')
    voices = pygame.mixer.Sound(f'levels/{level}/{level}_voices.ogg')

    with open(f'levels/{level}/{level}_labels.txt', 'r', encoding='utf-8') as lf:
        labels = [i.split('\t') for i in lf.read().split('\n')][:-1]

    # try:
        with open(f'levels\\{level}\\{level}_params.json', 'r') as params_file:
            params = json.load(params_file)
            background = Background(f'data\\sprites\\{params["BG"]}.png')
            player = AnimatedSprite(pygame.image.load(f'data\\sprites\\{params["PLAYER"]}.png'), 2, 1, 50, 50)

            # TODO: enemy = ...
    # except FileNotFoundError:
    #     background = Background('data\\sprites\\default_room.png')
    #     player = AnimatedSprite(pygame.image.load(f'data\\sprites\\missed_image.png'), 1, 1, HEIGHT / 2, WIDTH - 100)


    notes = {}
    for i in labels:
        let = i[-1]
        if let == '|':
            pl = True
            continue
        if pl:
            match let:
                case 'q':
                    let = 'й'
                case 'w':
                    let = 'ц'
                case 'e':
                    let = 'у'
                case 'r':
                    let = 'к'
        notes[(float(i[0]), float(i[1]))] = {'note': let, 'done': False}
    pygame.mixer.Channel(2).play(SOUNDS['loading'])


def count_score(x):  # TODO: Сделать НОРМАЛЬНЫЙ подсчет очков
    if abs(int((3 / x) * 100)) < 700:
        return abs(int((3 / x) * 100)) * 10
    else:
        return 700


def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n


def cord(s, t):
    return s * 200 - t * 200


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.phase = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        # self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.cur_frame = int(self.phase - len(self.frames) * (self.phase // len(self.frames)))
        self.image = self.frames[self.cur_frame]

class ParticleText():

    def __init__(self, pos, dx, dy, text, color='white'):
        self.font = pygame.font.SysFont('Comic Sans MS', 50)
        self.text = text
        self.color = color

        self.velocity = [dx, dy]
        self.x, self.y = self.pos = pos
        self.size = 50

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity * 10
        self.x += self.velocity[0] / 3000 * clock.get_time()/2
        self.y += self.velocity[1] / 3000 * clock.get_time()/2
        if self.pos not in RESOLUTION:
            del self

    def render(self, surface):
        rendered = self.font.render(self.text, True, self.color)
        surface.blit(rendered, (self.x, self.y))


# ~~~  ЫГРА  ~~~

pygame.init()
RESOLUTION = WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode(RESOLUTION)
pygame.display.set_icon(pygame.image.load('icon.png'))
clock = pygame.time.Clock()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
note_font = pygame.font.SysFont('Arial', 50)

SOUNDS = {}
for i in os.listdir('data/sounds'):
    SOUNDS[i[:-4]] = pygame.mixer.Sound(f'data/sounds\\{i}')


t = -1
play = False
player_input = set()
input_list = set()
score = 0
marks = []
do_voice = True
voice_vol = 1
load_level('Bobepoo')

all_sprites = pygame.sprite.Group()
background_group = pygame.sprite.Group()
all_sprites.add(player)
background_group.add(background)
background.target = 1

running = True
while running:
    player.phase = t * params['BPM'] / 60
    player.update()
    screen.fill('black')
    background_group.draw(screen)
    all_sprites.draw(screen)
    match background.target:
        case 0:
            background.rect.center = (WIDTH / 2, HEIGHT / 2)
            player.rect.center = (WIDTH / 2, HEIGHT / 2)
        case 1:
            background.rect.x = pygame.math.lerp(background.rect.x, -200, 0.0125)
            background.rect.y = pygame.math.lerp(background.rect.y, -100, 0.025)
            player.rect.x = pygame.math.lerp(player.rect.x, 500, 0.0125)
            player.rect.y = pygame.math.lerp(player.rect.y, 200, 0.025)
        case 2:
            background.rect.x = pygame.math.lerp(background.rect.x, 0, 0.0125)
            background.rect.y = pygame.math.lerp(background.rect.y, 0, 0.025)
            player.rect.x = pygame.math.lerp(player.rect.x, 700, 0.0125)
            player.rect.y = pygame.math.lerp(player.rect.y, 300, 0.025)

    # Ивенты
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # TODO: Меню там, выбор уровня сделать
        if event.type == pygame.KEYDOWN and event.dict['key'] == 32:
            play = not play
            t = -2
            if play:
                pygame.mixer.Channel(2).play(SOUNDS['321'])
            if not play:
                pygame.mixer.Channel(0).stop()
                pygame.mixer.Channel(1).stop()
                load_level(LEVEL)
                score = 0


        # Инпут
        if event.type == pygame.KEYDOWN:
            match event.dict['unicode']:
                case 'q' | 'й':
                    player_input.add('й')
                    input_list.add('й')
                case 'w' | 'ц':
                    player_input.add('ц')
                    input_list.add('ц')
                case 'e' | 'у':
                    player_input.add('у')
                    input_list.add('у')
                case 'r' | 'к':
                    player_input.add('к')
                    input_list.add('к')

        if event.type == pygame.KEYUP:
            match event.dict['unicode']:
                case 'q' | 'й':
                    input_list.remove('й')
                case 'w' | 'ц':
                    input_list.remove('ц')
                case 'e' | 'у':
                    input_list.remove('у')
                case 'r' | 'к':
                    input_list.remove('к')



    # Игровой цик
    if t >= 0 and not pygame.mixer.Channel(0).get_busy():
        pygame.mixer.Channel(0).play(music)
        pygame.mixer.Channel(1).play(voices)
    pygame.mixer.Channel(1).set_volume(voice_vol)
    if do_voice:
        voice_vol = 1
    else:
        voice_vol = 0
    if play:
        t += clock.get_time() / 1000
        for i in notes:
            for j in notes[i]['note']:
                if j in 'qwerty' and cord(i[0], t) + 100 < 100:
                    if not notes[i]['done']:
                        notes[i]['done'] = True
                        do_voice = True
                        background.target = 2
                if j in 'йцукен':
                    if not notes[i]['done']:
                        if cord(i[0], t) + 100 < 75:  # Таймаут
                            background.target = 1
                            if i[0] != i[1]:
                                pygame.mixer.Channel(2).play(SOUNDS['note_hold'])
                            else:
                                pygame.mixer.Channel(2).play(SOUNDS['note_miss'])
                            do_voice = False
                            score -= 200
                            marks.append(ParticleText((450, 300), random.uniform(-2000, 2000), -2000,
                                                      random.choice('Поздно/Не успел.../Ты опоздал!/Слишком долго...'
                                                                    '/ПРОСНИСЬ!/Не спи'.split('/')), color='grey'))

                            notes[i]['done'] = True
                        if 75 < cord(i[0], t) + 100 < 125:  # Попадание
                            background.target = 1
                            if player_input:
                                if player_input & set(j):
                                    score += count_score(cord(i[0], t))
                                    do_voice = True
                                    mark = random.choice('Попал/Работает/Хоть что-то/.../Старайся лучше'.split('/'))
                                    if 85 < cord(i[0], t) + 100 < 115:
                                        mark = random.choice('Неплох/Можно лучше./Пойдет/Сойдет/Норм'.split('/'))
                                    if 95 < cord(i[0], t) + 100 < 105:
                                        mark = random.choice('ИДЕАЛЬНО/В точку!/Ай да молодец!/16 Мегабайт!'.split('/'))
                                    marks.append(ParticleText((450, 300),
                                                              random.uniform(-2000, 2000), -2000, mark, color='yellow'))
                                else:  # Промах
                                    score -= 100
                                    do_voice = False
                                    marks.append(ParticleText((450, 300),
                                                              random.uniform(-2000, 2000), -2000,
                                                              random.choice('Мимо/Как так?/SyntaxError/'
                                                                            'Разуй глаза/Ну ты чё'.split('/')), color='red'))
                                    if i[0] != i[1]:
                                        pygame.mixer.Channel(2).play(SOUNDS['note_mishold'])
                                    else:
                                        pygame.mixer.Channel(2).play(SOUNDS['note_timeout'])
                                notes[i]['done'] = True
                                break

                if True:
                    match j:
                        case 'q':
                            offset = 50
                            pygame.draw.circle(screen, COLORS['q'], (offset, 100), 35, width=5)
                        case 'w':
                            offset = 125
                            pygame.draw.circle(screen, COLORS['w'], (offset, 100), 35, width=5)
                        case 'e':
                            offset = 200
                            pygame.draw.circle(screen, COLORS['e'], (offset, 100), 35, width=5)
                        case 'r':
                            offset = 275
                            pygame.draw.circle(screen, COLORS['r'], (offset, 100), 35, width=5)
                        case 'й':
                            offset = WIDTH - 275
                            if 'й' in input_list:
                                pygame.draw.circle(screen, 'grey', (offset, 100), 30)
                            else:
                                pygame.draw.circle(screen, COLORS['й'], (offset, 100), 35, width=5)
                        case 'ц':
                            offset = WIDTH - 200
                            if 'ц' in input_list:
                                pygame.draw.circle(screen, 'grey', (offset, 100), 30)
                            else:
                                pygame.draw.circle(screen, COLORS['ц'], (offset, 100), 35, width=5)
                        case 'у':
                            offset = WIDTH - 125
                            if 'у' in input_list:
                                pygame.draw.circle(screen, 'grey', (offset, 100), 30)
                            else:
                                pygame.draw.circle(screen, COLORS['у'], (offset, 100), 35, width=5)
                        case 'к':
                            offset = WIDTH - 50
                            if 'к' in input_list:
                                pygame.draw.circle(screen, 'grey', (offset, 100), 30)
                            else:
                                pygame.draw.circle(screen, COLORS['к'], (offset, 100), 35, width=5)
                        case None:
                            continue
                    if i[0] != i[1] and cord(i[1], t) > 0:
                        pygame.draw.line(screen, COLORS[j], (offset, clamp(cord(i[0], t) + 100, 100, 1000)),
                                         (offset, clamp(cord(i[1], t) + 100, 100, 1000)), width=10)
                    if j:
                        if not notes[i]['done']:
                            if cord(i[0], t) + 100 > 75:
                                pygame.draw.circle(screen, COLORS[j], (offset, cord(i[0], t) + 100), 30)
                                letter = note_font.render(j.upper(), False, 'black')
                                screen.blit(letter, (offset - 20, cord(i[0], t) + 100 - 25))
    time_surface = my_font.render(str(round(t, 2)), False, 'grey')
    score_note = my_font.render(str(score), True, 'grey')
    screen.blit(time_surface, (0, 0))
    screen.blit(score_note, (400, 300))
    for i in marks:
        i.update()
        i.render(screen)
    pygame.display.flip()
    player_input.clear()
    clock.tick(120)
