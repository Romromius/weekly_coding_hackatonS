import os
import random

import winsound

import pygame

COLORS = {'q': 'cyan', 'w': 'green', 'e': 'red', 'r': 'yellow',
          'й': 'cyan', 'ц': 'green', 'у': 'red', 'к': 'yellow'}
GRAVITY = 9.8
LEVEL = 2


class Background(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.target = 0


def lerp(x, y, s):
    return x * (1 - s) + y * s


def load_level(level):
    global music
    global voices
    global notes
    pl = False

    music = pygame.mixer.Sound(f'levels/{level}/music.ogg')
    voices = pygame.mixer.Sound(f'levels/{level}/voices.ogg')

    with open(f'levels/{level}/labels.txt', 'r', encoding='utf-8') as lf:
        labels = [i.split('\t') for i in lf.read().split('\n')][:-1]

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
    winsound.Beep(700, 200)


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


class ParticleText():

    def __init__(self, pos, dx, dy, text):
        self.font = pygame.font.SysFont('Comic Sans MS', 50)
        self.text = text

        self.velocity = [dx, dy]
        self.x, self.y = self.pos = pos
        self.size = 50

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self, tick=0.1):
        self.velocity[1] += self.gravity
        self.x += self.velocity[0] / 7000 * clock.get_time()/2
        self.y += self.velocity[1] / 7000 * clock.get_time()/2
        if self.pos not in RESOLUTION:
            del self

    def render(self, surface):
        rendered = self.font.render(self.text, True, 'white')
        surface.blit(rendered, (self.x, self.y))

# ЫГРА

pygame.init()
RESOLUTION = WIDTH, HEIGHT = 800, 600
pygame.init()
screen = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
note_font = pygame.font.SysFont('Arial', 50)

SOUNDS = {}
for i in os.listdir('data\\music'):
    SOUNDS[i[:-4]] = pygame.mixer.Sound(f'data\\music\\{i}')

load_level(LEVEL)

t = 0
play = False
player_input = set()
input_list = set()
score = 0
marks = []
do_voice = True
voice_vol = 1
pygame.mixer.Channel(2).set_volume(0.5)

all_sprites = pygame.sprite.Group()
background = Background('data\\sprites\\default_room.png')
all_sprites.add(background)

running = True
while running:
    screen.fill('black')
    all_sprites.draw(screen)
    match background.target:
        case 0:
            background.rect.center = (WIDTH / 2, HEIGHT / 2)
        case 1:
            background.rect.x = pygame.math.lerp(background.rect.x, -200, 0.02)
            background.rect.y = pygame.math.lerp(background.rect.y, -100, 0.02)
        case 2:
            background.rect.x = pygame.math.lerp(background.rect.x, 0, 0.02)
            background.rect.y = pygame.math.lerp(background.rect.y, 0, 0.02)
    print(background.rect.x)

    # Ивенты
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # TODO: Меню там, выбор уровня сделать
        if event.type == pygame.KEYDOWN and event.dict['key'] == 32:
            play = not play
            t = 0
            if play:
                pygame.mixer.Channel(0).play(music)
                pygame.mixer.Channel(1).play(voices)
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
    pygame.mixer.Channel(1).set_volume(voice_vol)
    if do_voice:
        voice_vol = 1
    else:
        voice_vol = 0
    pygame.draw.line(screen, 'red', (0, 100), (WIDTH, 100))
    if play:
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
                            marks.append(ParticleText((450, 300), random.uniform(-4000, 4000), -2000,
                                                      random.choice('Поздно/Не успел.../Ты опоздал!/Слишком долго...'
                                                                    '/ПРОСНИСЬ!/Не спи'.split('/'))))

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
                                                              random.uniform(-4000, 4000), -2000, mark))
                                else:  # Промах
                                    score -= 100
                                    do_voice = False
                                    marks.append(ParticleText((450, 300),
                                                              random.uniform(-4000, 4000), -2000,
                                                              random.choice('Мимо/Как так?/SyntaxError/'
                                                                            'Разуй глаза/Ну ты чё'.split('/'))))
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
                            pygame.draw.line(screen, 'grey', (offset, 0), (offset, HEIGHT))
                        case 'w':
                            offset = 125
                            pygame.draw.line(screen, 'grey', (offset, 0), (offset, HEIGHT))
                        case 'e':
                            offset = 200
                            pygame.draw.line(screen, 'grey', (offset, 0), (offset, HEIGHT))
                        case 'r':
                            offset = 275
                            pygame.draw.line(screen, 'grey', (offset, 0), (offset, HEIGHT))
                        case 'й':
                            offset = 50 + 450
                            pygame.draw.line(screen, 'grey', (offset, 0), (offset, HEIGHT))
                        case 'ц':
                            offset = 125 + 450
                            pygame.draw.line(screen, 'grey', (offset, 0), (offset, HEIGHT))
                        case 'у':
                            offset = 200 + 450
                            pygame.draw.line(screen, 'grey', (offset, 0), (offset, HEIGHT))
                        case 'к':
                            offset = 275 + 450
                            pygame.draw.line(screen, 'grey', (offset, 0), (offset, HEIGHT))
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
    time_surface = my_font.render(str(round(t, 2)), False, 'white')
    score_note = my_font.render(str(score), True, 'grey')
    screen.blit(time_surface, (0, 0))
    screen.blit(score_note, (400, 300))
    for i in marks:
        i.update()
        i.render(screen)
    pygame.display.flip()
    player_input.clear()
    clock.tick(120)
    t += clock.get_time() / 1000
