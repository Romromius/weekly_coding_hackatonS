import winsound

import pygame


def load_level(level):
    global music
    global voices
    global notes

    music = pygame.mixer.Sound(f'levels/{level}/music.ogg')
    voices = pygame.mixer.Sound(f'levels/{level}/voices.ogg')

    with open(f'levels/{level}/labels.txt', 'r', encoding='utf-8') as lf:
        labels = [i.split('\t') for i in lf.read().split('\n')][:-1]
        end = float(labels[-1][0])

    notes = {}
    for i in labels:
        notes[float(i[0])] = i[-1]
    winsound.Beep(700, 200)


pygame.init()
size = width, height = 800, 600
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


load_level(1)

t = 0
play = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.dict['key'] == 114:
            print('Start')
            play = True
            t = 0
            pygame.mixer.Channel(0).play(music)
            pygame.mixer.Channel(1).play(voices)
    t += clock.tick() / 1000
    screen.fill('black')
    pygame.draw.line(screen, 'red', (0, 100), (width, 100))
    if play:
        for i in notes:
            if i < t:
                continue
            for j in notes[i]:
                match j:
                    case 'a':
                        offset = 50
                    case 's':
                        offset = 125
                    case 'w':
                        offset = 200
                    case 'd':
                        offset = 275
                    case 'ф':
                        offset = 50 + 450
                    case 'ы':
                        offset = 125 + 450
                    case 'ц':
                        offset = 200 + 450
                    case 'в':
                        offset = 275 + 450
                    case _:
                        continue
                pygame.draw.circle(screen, 'white', (offset, i * 200 - t * 200 + 100), 10)
    pygame.display.flip()
