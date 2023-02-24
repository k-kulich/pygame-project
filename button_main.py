import sys
import pygame
from button_d import Button
from data_loader import load_image


def show_menu():
    SIZE = 800, 600

    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Main Menu")

    resume_b = load_image('resume_b.png')
    quit_b = load_image('exit_b.png')

    resume_button = Button(220, 230, resume_b, 1)
    quit_button = Button(470, 230, quit_b, 1)

    run = True
    while run:
        screen.fill(pygame.Color("BurlyWood"))
        if resume_button.draw(screen):
            return True, True
        if quit_button.draw(screen):
            return False, False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()


if __name__ == '__main__':
    show_menu()
