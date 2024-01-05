import winsound

import pygame


def load_level(level):
    global music
    global voices
    global notes

    music = pygame.mixer.Sound(f'levels/{level}/music.ogg')
    voices = pygame.mixer.Sound(f'levels/{level}/voices.ogg')

    notes = {}
    with open(f'levels/{level}/labels.txt', 'r', encoding='utf-8') as lf:
        labels = [i.split('\t') for i in lf.read().split('\n')][:-1]
        end = float(labels[-1][0])

    i = 0
    while i < end:
        notes[i] = []
        i += 0.25
    for i in labels:
        for j in notes:
            if j > float(i[0]):
                notes[j].append(i[-1])
                break
    winsound.Beep(700, 200)


pygame.init()
size = width, height = 800, 600
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


load_level(1)

t = 0
pygame.mixer.Channel(0).play(music)
pygame.mixer.Channel(1).play(voices)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    t += clock.tick() / 1000
    screen.fill('black')
    pygame.draw.line(screen, 'red', (0, 100), (width, 100))
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
                    offset = 50 + 400
                case 'ы':
                    offset = 125 + 400
                case 'ц':
                    offset = 200 + 400
                case 'в':
                    offset = 275 + 400
                case _:
                    continue
            pygame.draw.circle(screen, 'white', (offset, i * 200 - t * 200 + 100), 10)
    pygame.display.flip()
