import copy

import json

import math

import os

import random

import pygame

import sqlite3

pygame.init()

# Константы
RESOLUTION = WIDTH, HEIGHT = 800, 600
GRAVITY = 9.8
COLORS = {'q': 'cyan', 'w': 'green', 'e': 'red', 'r': 'yellow', 't': 'purple', 'y': 'blue',
          'й': 'cyan', 'ц': 'green', 'у': 'red', 'к': 'yellow', 'е': 'purple', 'н': 'blue'}
SOUNDS = {}
for i in os.listdir('data/sounds'):
    SOUNDS[i[:-4]] = pygame.mixer.Sound(f'data/sounds/{i}')
    print(SOUNDS)

font = pygame.font.Font(None, 66)

screen = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load('local_troubles/icon.png'))

# Глобальные переменные
sound_state = "1"
difficulty_state = "Джун"
# рекорды уровней
record1 = 0
record2 = 0
record3 = 0
record4 = 0
# БАЗА
db = sqlite3.connect('database_records.sqlite3')
cursor = db.cursor()

# Ивенты
start_event = pygame.USEREVENT + 1
options_event = pygame.USEREVENT + 2
back_event = pygame.USEREVENT + 3
change_theme_event = pygame.USEREVENT + 4
play_event = pygame.USEREVENT + 5
bobepoo_event = pygame.USEREVENT + 6
cat_event = pygame.USEREVENT + 7
dog_event = pygame.USEREVENT + 8
shark_event = pygame.USEREVENT + 9
ScoreBoard_event = pygame.USEREVENT + 10
change_sounds_event = pygame.USEREVENT + 11
change_difficulty_event = pygame.USEREVENT + 12


def count_score(x):
    if ((-x ** 2 / 10) + 3) * 700 < 700:
        return abs(int((3 / x) * 100)) * 10
    else:
        return 700


def cord(s, t, bpm):
    return s * bpm * 3 - t * bpm * 3


def roundate(n, range: tuple):
    if n < range[0]:
        return range[0]
    if n > range[1]:
        return range[1]
    return n


class Background(pygame.sprite.Sprite):
    def __init__(self, image: str):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.target = 0


class ParticleText():

    def __init__(self, pos, dx, dy, text, color='white', size=50):
        self.font = pygame.font.SysFont('Comic Sans MS', size)
        self.text = text
        self.color = color

        self.vx, self.vy = dx, dy
        self.pos = self.x, self.y = pos
        self.size = size

    def update(self, time):
        self.vy += GRAVITY * 10
        self.x += self.vx * time / 5000
        self.y += self.vy * time / 5000
        if self.pos not in RESOLUTION:
            del self

    def render(self, surface):
        surface.blit(self.font.render(self.text, True, self.color), (self.x, self.y))


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, idles):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.phase = 0
        self.idles = idles

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.phase > self.idles:
            self.phase = 0
        self.image = self.frames[self.phase]

    def liteUpdate(self):
        self.image = self.frames[self.phase]


class Button:
    def __init__(self, x, y, w, h, text, event, align='center',
                 image_path="data/sprites/empty.png",
                 indic_path1="data/sprites/button_bckgrnd1.png",
                 indic_path2="data/sprites/button_bckgrnd2.png",
                 pref=None):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.text = text
        self.fl = False
        # self.sp = [indic_path1, indic_path2]
        self.align = align
        self.pref = pref

        self.image = pygame.image.load(image_path)

        self.indic_image1 = pygame.image.load(indic_path1)
        self.indic_image2 = pygame.image.load(indic_path2)

        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_indic = False
        self.event = event

        self.rolloversound = pygame.mixer.Sound('local_troubles/data/sounds/buttonrollover.wav')
        self.clocksound = pygame.mixer.Sound('local_troubles/data/sounds/buttonclickrelease.wav')

    def draw(self, surface):
        if self.is_indic:
            if self.fl:
                img = self.indic_image1
            if not self.fl:
                img = self.indic_image2
            # img = pygame.image.load(self.sp[int(self.phase - 2 * (self.phase // 2))])
            self.fl = not self.fl
        else:
            img = self.image
        surface.blit(img, self.rect.topleft)
        text_surface = font.render(self.text, True, 'grey')
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_indic(self, pos_mouse):
        if not self.is_indic and self.rect.collidepoint(pos_mouse):
            self.rolloversound.play()
        self.is_indic = self.rect.collidepoint(pos_mouse)

    def click_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_indic:
            if sound_state == "1":
                print("ТЫК")
                self.clocksound.play()
            print(f"Внимание! Была! Нажата! Кнопка! {self.text}!")
            pygame.event.post(pygame.event.Event(self.event, button=self))


def welcome_window():
    def_background = pygame.image.load('data/sprites/welcome_window_background.png')
    screen.fill((100, 10, 100))
    text = font.render("нажмите любую кнопку", 1, (255, 255, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()
            if any(pygame.key.get_pressed()) and not pygame.key.get_pressed()[pygame.K_ESCAPE]:
                return

        screen.blit(def_background, (0, 0))
        screen.blit(text, (0, 0))
        pygame.display.flip()


def main_menu():
    global musics
    clock = pygame.time.Clock()
    def_background = pygame.image.load('data/sprites/start_window_background.png')
    background = def_background
    musics = ['menu_theme_1.mp3|50', 'menu_theme_2.wav|100', 'menu_theme_3.wav|200']

    with open('local_troubles/settings.json', 'r') as settings_file:
        settings = json.load(settings_file)
        settings['bpm'] = int(musics[settings['theme']][musics[settings['theme']].index('|') + 1:])

    pygame.mixer.music.load(f'data/sounds/{musics[settings["theme"]][:musics[settings["theme"]].index("|")]}')
    pygame.mixer.music.play(loops=-1)
    scale = 2
    default_rect = def_background.get_rect()
    t = 0
    phase = int(t * settings['bpm'] / 60)

    start_button = Button(WIDTH / 2 - 382 / 2, HEIGHT / 5, 0, 0, "Играть", start_event)
    options_button = Button(WIDTH / 2 - 382 / 2, HEIGHT / 3, 0, 0, "Настройки", options_event)
    exit_button = Button(WIDTH / 2 - 382 / 2, HEIGHT / 1.2, 0, 0, "Выйти", pygame.QUIT)
    buttons = [start_button, options_button, exit_button]

    running = True
    while running:
        screen.fill('black')
        t += clock.get_time() / 1000
        last_phase = phase
        phase = int(t * settings['bpm'] / 60)

        if phase != last_phase:
            scale = 1.4
        scale = pygame.math.lerp(scale, 1, 0.05)
        background = pygame.transform.scale(def_background,
                                            (pygame.math.lerp(background.get_width(),
                                                              def_background.get_width() * scale,
                                                              roundate(clock.get_time() / 100, (0, 1))),
                                             pygame.math.lerp(background.get_height(),
                                                              def_background.get_height() * scale,
                                                              roundate(clock.get_time() / 100, (0, 1)))))

        screen.blit(background, ((background.get_width() - WIDTH) / -2, (background.get_height() - HEIGHT) / -2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()
            if event.type == options_event:
                settings = options(settings, musics)
            if event.type == start_event:
                freeplay(settings, musics)

            for i in buttons:
                i.click_event(event)

        for i in buttons:
            i.check_indic(pygame.mouse.get_pos())
            i.draw(screen)

        clock.tick(120)
        pygame.display.flip()


def freeplay(settings, musics):
    clock = pygame.time.Clock()
    def_background = pygame.image.load('data/sprites/begin_window_background.png')
    background = def_background
    scale = 1.4
    t = 0
    phase = int(t * settings['bpm'] / 60)

    botan_button = Button(WIDTH / 3.5, HEIGHT / 7, 0, 0, "Botan", bobepoo_event)
    record = font.render(str(record1), 1, "blue")
    cat_button = Button(WIDTH / 3.5, HEIGHT / 3.5, 0, 0, "Kot", cat_event)
    dog_button = Button(WIDTH / 3.5, HEIGHT / 2.8, 0, 0, "Sobala", dog_event)
    # shark_button = Button(WIDTH / 3.5, HEIGHT / 2, 0, 0, "", shark_event)
    back_button = Button(WIDTH / 3.5, HEIGHT / 1.2, 0, 0, "Назад", back_event)

    buttons = [botan_button, cat_button, dog_button, back_button]

    running = True
    while running:
        screen.fill('black')
        t += clock.get_time() / 1000
        last_phase = phase
        phase = int(t * settings['bpm'] / 60)

        if phase != last_phase:
            scale = 1.4
        scale = pygame.math.lerp(scale, 1, 0.05)
        background = pygame.transform.scale(def_background,
                                            (pygame.math.lerp(background.get_width(),
                                                              def_background.get_width() * scale,
                                                              roundate(clock.get_time() / 100, (0, 1))),
                                             pygame.math.lerp(background.get_height(),
                                                              def_background.get_height() * scale,
                                                              roundate(clock.get_time() / 100, (0, 1)))))

        screen.blit(background, ((background.get_width() - WIDTH) / -2, (background.get_height() - HEIGHT) / -2))
        txt_bobepoo = font.render(str(record1), 1, "blue")
        screen.blit(txt_bobepoo, (720, 88))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

            if event.type == back_event:
                return

            if event.type == bobepoo_event:
                level(settings, 'Bobepoo')

            if event.type == cat_event:
                level(settings, 'Blammed')

            if event.type == dog_event:
                level(settings, 'Thorns')

            for i in buttons:
                i.click_event(event)


        for i in buttons:
            i.check_indic(pygame.mouse.get_pos())

            i.draw(screen)

        clock.tick(120)
        pygame.display.flip()


def level(settings, lvl):
    global record1, record2, record3, record4
    pygame.mixer.music.stop()
    pygame.mixer.stop()
    clock = pygame.time.Clock()

    # Load level
    music = pygame.mixer.Sound(f'levels/{lvl}/{lvl}_music.ogg')
    voices = pygame.mixer.Sound(f'levels/{lvl}/{lvl}_voices.ogg')
    with open(f'levels/{lvl}/{lvl}_labels.txt', 'r', encoding='utf-8') as lf:
        labels = [i.split('\t') for i in lf.read().split('\n')][:-1]
    with open(f'levels/{lvl}/{lvl}_params.json', 'r') as params_file:
        params = json.load(params_file)
        background = Background(f'data/sprites/{params["BG"]}.png')
        player = AnimatedSprite(pygame.image.load(f'data/sprites/{params["PLAYER"]}.png'), 3, 2, 800, 600, 1)
        enemy = AnimatedSprite(pygame.image.load(f'data/sprites/{params["ENEMY"]}.png'), 3, 2, 0, 600, 1)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(enemy)
    notes = {}

    read_pl = False
    for i in labels:
        let = i[-1]
        if let == '|':
            read_pl = True
            continue
        if read_pl:
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

    t = -2
    # play = False
    player_input = set()
    input_list = set()
    score = 0
    marks = []
    do_voice = True
    voice_vol = 1
    background_group = pygame.sprite.Group()
    background_group.add(background)
    background.target = 1
    SOUNDS['321'].play()

    phase = int(t * settings['bpm'] / 60)

    running = True
    play = True
    playing = False
    while running:

        last_phase = phase
        phase = int(t * params['BPM'] / 60)
        if phase != last_phase:
            player.phase += 1
            player.update()
            enemy.phase += 1
            enemy.update()
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
                enemy.rect.x = pygame.math.lerp(enemy.rect.x, -100, 0.0125)
                enemy.rect.y = pygame.math.lerp(enemy.rect.y, 200, 0.025)
            case 2:
                background.rect.x = pygame.math.lerp(background.rect.x, 0, 0.0125)
                background.rect.y = pygame.math.lerp(background.rect.y, 0, 0.025)
                player.rect.x = pygame.math.lerp(player.rect.x, 700, 0.0125)
                player.rect.y = pygame.math.lerp(player.rect.y, 300, 0.025)
                enemy.rect.x = pygame.math.lerp(enemy.rect.x, 100, 0.0125)
                enemy.rect.y = pygame.math.lerp(enemy.rect.y, 300, 0.025)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.Channel(1).stop()
                return

            # if event.type == pygame.KEYDOWN and event.dict['key'] == 32:
            #     play = not play
            #     t = -2
            #     if play:
            #         pygame.mixer.Channel(2).play(SOUNDS['321'])
            #     if not play:
            #         pygame.mixer.Channel(0).stop()
            #         pygame.mixer.Channel(1).stop()
            #         load_level(LEVEL)
            #         score = 0

            # Инпут
            if event.type == pygame.KEYDOWN:
                match event.dict['unicode']:
                    case 'q' | 'й':
                        player_input.add('й')
                        input_list.add('й')
                        player.phase = 2
                        player.liteUpdate()
                    case 'w' | 'ц':
                        player_input.add('ц')
                        input_list.add('ц')
                        player.phase = 3
                        player.liteUpdate()
                    case 'e' | 'у':
                        player_input.add('у')
                        input_list.add('у')
                        player.phase = 4
                        player.liteUpdate()
                    case 'r' | 'к':
                        player_input.add('к')
                        input_list.add('к')
                        player.phase = 5
                        player.liteUpdate()

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
        if t >= 0 and not pygame.mixer.Channel(0).get_busy() and not playing:
            pygame.mixer.Channel(0).play(music)
            pygame.mixer.Channel(1).play(voices)
            playing = True
        pygame.mixer.Channel(1).set_volume(voice_vol)
        if do_voice:
            voice_vol = 1
        else:
            voice_vol = 0
        if play:
            t += clock.get_time() / 1000
            for i in notes:
                for j in notes[i]['note']:
                    if j in 'qwerty' and cord(i[0], t, params['BPM']) + 100 < 100:
                        if not notes[i]['done']:
                            notes[i]['done'] = True
                            do_voice = True
                            background.target = 2
                            enemy.update()
                            match notes[i]['note']:
                                case 'q':
                                    enemy.phase = 2
                                    enemy.liteUpdate()
                                case 'w':
                                    enemy.phase = 3
                                    enemy.liteUpdate()
                                case 'e':
                                    enemy.phase = 4
                                    enemy.liteUpdate()
                                case 'r':
                                    enemy.phase = 5
                                    enemy.liteUpdate()

                    if j in 'йцукен':
                        if not notes[i]['done']:
                            if cord(i[0], t, params['BPM']) + 100 < 75:  # Таймаут
                                background.target = 1
                                if i[0] != i[1]:
                                    pygame.mixer.Channel(2).play(SOUNDS['note_hold'])
                                else:
                                    pygame.mixer.Channel(2).play(SOUNDS['note_miss'])
                                do_voice = False
                                score -= 200
                                marks.append(ParticleText((450, 300), random.uniform(-2000, 2000), -2000,
                                                          random.choice(
                                                              'Поздно/Не успел.../Ты опоздал!/Слишком долго...'
                                                              '/ПРОСНИСЬ!/Не спи'.split('/')), color='grey'))

                                notes[i]['done'] = True
                            if 75 < cord(i[0], t, params['BPM']) + 100 < 125:  # Попадание
                                background.target = 1
                                if player_input:
                                    if player_input & set(j):
                                        score += count_score(cord(i[0], t, params['BPM']))
                                        do_voice = True
                                        mark = random.choice('Попал/Работает/Хоть что-то/.../Старайся лучше'.split('/'))
                                        if 85 < cord(i[0], t, params['BPM']) + 100 < 115:
                                            mark = random.choice('Неплох/Можно лучше./Пойдет/Сойдет/Норм'.split('/'))
                                        if 95 < cord(i[0], t, params['BPM']) + 100 < 105:
                                            mark = random.choice(
                                                'ИДЕАЛЬНО/В точку!/Ай да молодец!/16 Мегабайт!'.split('/'))
                                        marks.append(ParticleText((450, 300),
                                                                  random.uniform(-2000, 2000), -2000, mark,
                                                                  color='yellow'))
                                    else:  # Промах
                                        score -= 100
                                        do_voice = False
                                        marks.append(ParticleText((450, 300),
                                                                  random.uniform(-2000, 2000), -2000,
                                                                  random.choice('Мимо/Как так?/SyntaxError/'
                                                                                'Разуй глаза/Ну ты чё'.split('/')),
                                                                  color='red'))
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
                                pygame.draw.circle(screen, COLORS['q'], (offset, 100), 30, width=5)
                            case 'w':
                                offset = 110
                                pygame.draw.circle(screen, COLORS['w'], (offset, 100), 30, width=5)
                            case 'e':
                                offset = 170
                                pygame.draw.circle(screen, COLORS['e'], (offset, 100), 30, width=5)
                            case 'r':
                                offset = 230
                                pygame.draw.circle(screen, COLORS['r'], (offset, 100), 30, width=5)
                            case 't':
                                offset = 290
                                pygame.draw.circle(screen, COLORS['t'], (offset, 100), 30, width=5)
                            case 'y':
                                offset = 350
                                pygame.draw.circle(screen, COLORS['y'], (offset, 100), 30, width=5)
                            case 'й':
                                offset = WIDTH - 275
                                if 'й' in input_list:
                                    pygame.draw.circle(screen, 'grey', (offset, 100), 25)
                                else:
                                    pygame.draw.circle(screen, COLORS['й'], (offset, 100), 30, width=5)
                            case 'ц':
                                offset = WIDTH - 200
                                if 'ц' in input_list:
                                    pygame.draw.circle(screen, 'grey', (offset, 100), 25)
                                else:
                                    pygame.draw.circle(screen, COLORS['ц'], (offset, 100), 30, width=5)
                            case 'у':
                                offset = WIDTH - 125
                                if 'у' in input_list:
                                    pygame.draw.circle(screen, 'grey', (offset, 100), 25)
                                else:
                                    pygame.draw.circle(screen, COLORS['у'], (offset, 100), 30, width=5)
                            case 'к':
                                offset = WIDTH - 50
                                if 'к' in input_list:
                                    pygame.draw.circle(screen, 'grey', (offset, 100), 25)
                                else:
                                    pygame.draw.circle(screen, COLORS['к'], (offset, 100), 30, width=5)
                            case None:
                                continue
                        if i[0] != i[1] and cord(i[1], t, params['BPM']) > 0:
                            pygame.draw.line(screen, COLORS[j],
                                             (offset, roundate(cord(i[0], t, params['BPM']) + 100, (100, 1000))),
                                             (offset, roundate(cord(i[1], t, params['BPM']) + 100, (100, 1000))),
                                             width=10)
                        if j:
                            if not notes[i]['done']:
                                if cord(i[0], t, params['BPM']) + 100 > 75:
                                    pygame.draw.circle(screen, COLORS[j], (offset, cord(i[0], t, params['BPM']) + 100),
                                                       30)
                                    letter = font.render(j.upper(), False, 'black')
                                    screen.blit(letter, (offset - 20, cord(i[0], t, params['BPM']) + 100 - 25))
        time_surface = font.render(str(round(t, 2)), False, 'grey')
        score_note = font.render(str(score), True, 'grey')
        screen.blit(time_surface, (0, 0))
        screen.blit(score_note, (400, 300))
        for mark_par in marks:
            mark_par.update(clock.get_time())
            mark_par.render(screen)
        player_input.clear()
        if score < -1000 or not pygame.mixer.Channel(0).get_busy():  # ПРОИГРЫШ / КОНЧИЛОСЬ ВРЕМЯ
            pygame.mixer.Channel(0).stop()
            pygame.mixer.Channel(1).stop()
            pygame.mixer.music.play(loops=-1)
            background = pygame.image.load('data/sprites/result.png')
            txt_results = font.render("ТЕКУЩИЙ РЕКОРД: " + str(score), 1, "red")
            back_button = Button(WIDTH / 3.5, HEIGHT / 3, 0, 0, "Назад", back_event)
            # cursor.execute(f'SELECT * FROM records WHERE level={str(lvl)}')

            running = True
            while running:
                screen.blit(background, (0, 0))
                screen.blit(txt_results, (100, 100))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        quit()
                    if event.type == back_event:
                        return
                    back_button.click_event(event)

                back_button.check_indic(pygame.mouse.get_pos())
                back_button.draw(screen)

                pygame.display.flip()
            if score > 0:
                match lvl:
                    case "Bobepoo":
                        record1 = max(record1, score)
                    case 2:
                        record2 = max(record2, score)
                    case 3:
                        record3 = max(record3, score)
                    case 4:
                        record4 = max(record4, score)

            # pygame.mixer.music.load(f'data/sounds/{musics[settings["theme"]][:musics[settings["theme"]].index("|")]}')
            pygame.mixer.music.play(loops=-1)
            return

        clock.tick(120)
        pygame.display.flip()


def options(settings, musics):
    global difficulty_state, sound_state
    txt_diff = font.render(difficulty_state, 1, "grey")
    txt_sound = font.render(sound_state, 1, "grey")

    clock = pygame.time.Clock()
    def_background = pygame.image.load('data/sprites/default_room.png')
    background = def_background
    scale = 1.4
    t = 0
    phase = int(t * settings['bpm'] / 60)

    start_button = Button(WIDTH / 3.5, HEIGHT / 6, 0, 0, "Сменить тему", change_theme_event)
    difficulty_button = Button(WIDTH / 3.5, HEIGHT / 3, 0, 0, "Слож-сть:", change_difficulty_event)
    sounds_button = Button(WIDTH / 3.5, HEIGHT / 2, 0, 0, "Звуки:", change_sounds_event)
    back_button = Button(WIDTH / 3.5, HEIGHT / 1.2, 0, 0, "Назад", back_event)
    buttons = [start_button, difficulty_button, sounds_button, back_button]

    running = True
    while running:
        screen.fill('black')
        t += clock.get_time() / 1000
        last_phase = phase
        phase = int(t * settings['bpm'] / 60)

        if phase != last_phase:
            scale = 1.4
        scale = pygame.math.lerp(scale, 1, 0.05)
        background = pygame.transform.scale(def_background,
                                            (pygame.math.lerp(background.get_width(),
                                                              def_background.get_width() * scale,
                                                              roundate(clock.get_time() / 100, (0, 1))),
                                             pygame.math.lerp(background.get_height(),
                                                              def_background.get_height() * scale,
                                                              roundate(clock.get_time() / 100, (0, 1)))))

        screen.blit(background, ((background.get_width() - WIDTH) / -2, (background.get_height() - HEIGHT) / -2))
        screen.blit(txt_diff, (620, 200))
        screen.blit(txt_sound, (620, 300))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

            if event.type == back_event:
                return settings

            if event.type == change_difficulty_event:
                if difficulty_state == "Джун":
                    difficulty_state = "Сеньор"
                else:
                    difficulty_state = "Джун"
                txt_diff = font.render(difficulty_state, 1, "grey")

            if event.type == change_sounds_event:
                if sound_state == "1":
                    sound_state = "0"
                else:
                    sound_state = "1"
                txt_sound = font.render(sound_state, 1, "grey")

            if event.type == change_theme_event:
                pygame.mixer.stop()
                settings['theme'] += 1
                if settings['theme'] > len(musics) - 1:
                    settings['theme'] = 0
                settings['bpm'] = int(musics[settings["theme"]][musics[settings["theme"]].index("|") + 1:])
                with open('local_troubles/settings.json', 'w') as settings_file:
                    json.dump(settings, settings_file)
                pygame.mixer.music.load(
                    f'data/sounds/{musics[settings["theme"]][:musics[settings["theme"]].index("|")]}')
                pygame.mixer.music.play(loops=-1)

            for i in buttons:
                i.click_event(event)

        for i in buttons:
            i.check_indic(pygame.mouse.get_pos())
            i.draw(screen)

        clock.tick(120)
        pygame.display.flip()


if __name__ == '__main__':
    welcome_window()
    main_menu()
