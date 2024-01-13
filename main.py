import random

import winsound

import pygame

COLORS = {'q': 'cyan', 'w': 'green', 'e': 'red', 'r': 'yellow',
          'й': 'cyan', 'ц': 'green', 'у': 'red', 'к': 'yellow'}
GRAVITY = 9.8
LEVEL = 2

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
        letter = i[-1]
        if letter == '|':
            pl = True
            continue
        if pl:
            match letter:
                case 'q':
                    letter = 'й'
                case 'w':
                    letter = 'ц'
                case 'e':
                    letter = 'у'
                case 'r':
                    letter = 'к'
        notes[float(i[0])] = letter
    winsound.Beep(700, 200)
    print(notes)


def count_score(x):
    if abs(int((3 / x) * 100)) < 500:
        return abs(int((3 / x) * 100))
    else:
        return 500


class ParticleText():

    def __init__(self, pos, dx, dy, text):
        self.my_font = pygame.font.SysFont('Comic Sans MS', 50)
        self.text = text

        self.velocity = [dx, dy]
        self.x, self.y = self.pos = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self, tick=0.1):
        self.velocity[1] += self.gravity
        self.x += self.velocity[0] / 7000
        self.y += self.velocity[1] / 7000
        if self.pos not in size:
            del self

    def render(self, surface):
      rendered = self.my_font.render(self.text, True, 'white')
      surface.blit(rendered, (self.x, self.y))


pygame.init()
size = width, height = 800, 600
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)


load_level(LEVEL)

t = 0
play = False
player_input = set()
input_list = set()
score = 0
marks = []

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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


    t += clock.tick() / 1000
    screen.fill('black')
    pygame.draw.line(screen, 'red', (0, 100), (width, 100))
    if play:
        for i in notes:
            if notes[i] is None:
                continue
            for j in notes[i]:
                if j in 'qwerty' and i * 200 - t * 200 + 100 < 100:
                    notes[i] = None
                    continue
                if j in 'йцукен':
                    if i * 200 - t * 200 + 100 < 75:
                        print('miss')
                        score -= 200
                        marks.append(ParticleText((450, 300), random.uniform(-4000, 4000), -3000, 'Не спи'))

                        notes[i] = None
                        continue
                    if 75 < i * 200 - t * 200 + 100 < 125:
                        if player_input:
                            if player_input & set(j):
                                score += count_score(i * 200 - t * 200)
                                mark = 'Попал'
                                if 85 < i * 200 - t * 200 + 100 < 115:
                                    mark = 'Неплох'
                                if 95 < i * 200 - t * 200 + 100 < 105:
                                    mark = 'ИДЕАЛЬНО'
                                marks.append(ParticleText((450, 300), random.uniform(-4000, 4000), -3000, mark))
                            else:
                                score -= 100
                                marks.append(ParticleText((450, 300), random.uniform(-4000, 4000), -3000, 'Лох'))
                            notes[i] = None
                            break

                if j is not None:
                    match j:
                        case 'q':
                            offset = 50
                        case 'w':
                            offset = 125
                        case 'e':
                            offset = 200
                        case 'r':
                            offset = 275
                        case 'й':
                            offset = 50 + 450
                        case 'ц':
                            offset = 125 + 450
                        case 'у':
                            offset = 200 + 450
                        case 'к':
                            offset = 275 + 450
                        case None:
                            continue
                    if j:
                        pygame.draw.circle(screen, COLORS[j], (offset, i * 200 - t * 200 + 100), 20)
    time_surface = my_font.render(str(round(t, 2)), False, 'white')
    score_note = my_font.render(str(score), True, 'grey')
    screen.blit(time_surface, (0, 0))
    screen.blit(score_note, (400, 300))
    for i in marks:
        i.update()
        i.render(screen)
    pygame.display.flip()
    player_input.clear()
