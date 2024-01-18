import copy
import json
import math

import pygame

pygame.init()

# Константы
RESOLUTION = WIDTH, HEIGHT = 800, 600
GRAVITY = 9.8
COLORS = {'q': 'cyan', 'w': 'green', 'e': 'red', 'r': 'yellow',
          'й': 'cyan', 'ц': 'green', 'у': 'red', 'к': 'yellow'}
T = 0


screen = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load('icon.png'))

start_event = pygame.USEREVENT + 1
options_event = pygame.USEREVENT + 2
back_event = pygame.USEREVENT + 3
change_theme_event = pygame.USEREVENT + 4


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

        self.velocity = self.vx, self.vy = dx, dy
        self.pos = self.x, self.y = pos
        self.size = size

    def update(self):
        self.velocity[1] += GRAVITY * 10
        self.x += self.vx * clock.get_time()
        self.y += self.vy * clock.get_time()
        if self.pos not in RESOLUTION:
            del self

    def render(self, surface):
        surface.blit(self.font.render(self.text, True, self.color), (self.x, self.y))


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


class Button:
    def __init__(self, x, y, w, h, text, event, align='center',
                 image_path="data\\sprites\\empty.png",
                 indic_path1="data\\sprites\\button_bckgrnd1.png",
                 indic_path2="data\\sprites\\button_bckgrnd2.png"):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.text = text
        self.phase = T
        self.sp = [indic_path1, indic_path2]
        self.align = align

        self.image = pygame.image.load(image_path)

        self.indic_image1 = pygame.image.load(indic_path1)
        self.indic_image2 = pygame.image.load(indic_path2)

        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_indic = False
        self.event = event

        self.rolloversound = pygame.mixer.Sound('data\\sounds\\buttonrollover.wav')
        self.clocksound = pygame.mixer.Sound('data\\sounds\\buttonclickrelease.wav')

    def draw(self, surface):
        if self.is_indic:
            img = pygame.image.load(self.sp[int(self.phase - 2 * (self.phase // 2))])
        else:
            img = self.image
        surface.blit(img, self.rect.topleft)

        font = pygame.font.Font(None, 66)
        text_surface = font.render(self.text, True, 'grey')
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_indic(self, pos_mouse):
        if not self.is_indic and self.rect.collidepoint(pos_mouse):
            self.rolloversound.play()
        self.is_indic = self.rect.collidepoint(pos_mouse)

    def click_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_indic:
            self.clocksound.play()
            print(f"Внимание! Была! Нажата! Кнопка! {self.text}!")
            pygame.event.post(pygame.event.Event(self.event, button=self))


def main_menu():
    clock = pygame.time.Clock()
    def_background = pygame.image.load('data\\sprites\\start_window_background.png')
    background = def_background
    musics = ['menu_theme_1.wav|100', 'menu_theme_2.wav|100', 'menu_theme_3.wav|200']

    with open('settings.json', 'r') as settings_file:
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
                                                              roundate(clock.get_time()/100, (0, 1))),
                                             pygame.math.lerp(background.get_height(),
                                                              def_background.get_height() * scale,
                                                              roundate(clock.get_time()/100, (0, 1)))))

        screen.blit(background, ((background.get_width() - WIDTH) / -2, (background.get_height() - HEIGHT) / -2))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()
            if event.type == options_event:
                settings = options(settings, musics)
            for i in buttons:
                i.click_event(event)

        for i in buttons:
            i.check_indic(pygame.mouse.get_pos())
            i.draw(screen)


        clock.tick(120)
        pygame.display.flip()


def options(settings, musics):
    clock = pygame.time.Clock()
    def_background = pygame.image.load('data\\sprites\\default_room.png')
    background = def_background
    scale = 1.4
    t = 0
    phase = int(t * settings['bpm'] / 60)

    start_button = Button(WIDTH / 3.5, HEIGHT / 5, 0, 0, "Сменить тему", change_theme_event)
    options_button = Button(WIDTH / 3.5, HEIGHT / 3, 0, 0, "Ничего не делать", pygame.USEREVENT)
    back_button = Button(WIDTH / 3.5, HEIGHT / 2, 0, 0, "Назад", back_event)
    buttons = [start_button, options_button, back_button]

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
                                                              roundate(clock.get_time()/100, (0, 1))),
                                             pygame.math.lerp(background.get_height(),
                                                              def_background.get_height() * scale,
                                                              roundate(clock.get_time()/100, (0, 1)))))

        screen.blit(background, ((background.get_width() - WIDTH) / -2, (background.get_height() - HEIGHT) / -2))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

            if event.type == back_event:
                return settings

            if event.type == change_theme_event:
                settings['theme'] += 1
                if settings['theme'] > len(musics) - 1:
                    settings['theme'] = 0
                settings['bpm'] = int(musics[settings["theme"]][musics[settings["theme"]].index("|") + 1:])
                with open('settings.json', 'w') as settings_file:
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
    main_menu()