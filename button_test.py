import pygame


class Button:
    def __init__(self, x, y, w, h, text, image_path="data\\sprites\\empty.png",
                 indic_path1="data\\sprites\\button_bckgrnd1.png",
                 indic_path2="data\\sprites\\button_bckgrnd2.png",
                 sound_path='data\\sounds\\q.ogg'):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.text = text
        self.fl = 0

        self.image = pygame.image.load(image_path)

        self.indic_image1 = pygame.image.load(indic_path1)
        self.indic_image2 = pygame.image.load(indic_path2)

        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.sound = None
        if sound_path:
            # <<<<<<<<<<<<<<<<<ЧЕКНЕШЬ?>>>>>>>>>>>>>>>>>>>
            self.sound = pygame.mixer.Sound(sound_path)
        self.is_indic = False

    def draw(self, screen):
        if self.is_indic:
            if not self.fl:
                img = self.indic_image1
            else:
                img = self.indic_image2
            self.fl = not self.fl
        else:
            img = self.image
        screen.blit(img, self.rect.topleft)

        font = pygame.font.Font(None, 66)
        text_surface = font.render(self.text, True, (0, 100, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_indic(self, pos_mouse):
        self.is_indic = self.rect.collidepoint(pos_mouse)

    def click_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_indic:
            if self.sound:
                self.sound.play()
            print(f"была нажата кнопка {self.text}")


        # pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self)) <НА СЛУЧАЙ ПЕРСОНАЛЬНЫХ ЕВЕНТОВ>

pygame.init()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)
ICON = pygame.image.load("icon.png")
pygame.display.set_icon(ICON)


def main_menu():
    BACK = pygame.image.load("data/sprites/start_window_background.png")

    # КНОПКИ СОЗДАНИЕ
    # <<<<<<<<<<<<<<<<<<<<<<<<ЛЮБЫЕ ПУТИ К ЗВУКАМ - ПОСЛЕДНИЙ АРГУМЕНТ>>>>>>>>>>>>>>>>
    start_button = Button(width / 3.5, height / 5, 0, 0, "начать игру")
    options_button = Button(width / 3.5, height / 3, 0, 0, "настройки")
    exit_button = Button(width / 3.5, height / 2, 0, 0, "выйти")
    buttons = [start_button, options_button, exit_button]

    running = True
    while running:
        screen.blit(BACK, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            for i in buttons:
                i.click_event(event)

        for i in buttons:
            i.check_indic(pygame.mouse.get_pos())
            i.draw(screen)
        pygame.display.flip()


def settings():
    BACK = pygame.image.load("data/sprites/begin_window_background.png")
    # КНОПКИ СОЗДАНИЕ
    difficulty_button = Button(width / 3, height / 5, 0, 0, "сложность:", "data/sprites/empty.png", "button_bckgrnd1.png", "button_bckgrnd2.png")
    theme_button = Button(width / 3, height / 3.5, 0, 0, "тема:", "data/sprites/empty.png", "button_bckgrnd1.png", "button_bckgrnd2.png")
    sissounds_button = Button(width / 3.5, height / 2.7, 0, 0, "СИС.ЗВУКИ: ", "data/sprites/empty.png", "button_bckgrnd1.png", "button_bckgrnd2.png")

    running = True
    while running:
        screen.blit(BACK, (0, 0))


def exit_window():
    pygame.quit()


if __name__ == "__main__":
    main_menu()
pygame.quit()