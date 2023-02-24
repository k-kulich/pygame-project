import pygame
import button_d


def show_menu():
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Main Menu")

    resume_b = pygame.image.load("images/resume_b.png")
    quit_b = pygame.image.load("images/exit_b.png")

    resume_button = button_d.Button(220, 230, resume_b, 1)
    quit_button = button_d.Button(470, 230, quit_b, 1)

    run = True
    while run:
        screen.fill(pygame.Color("BurlyWood"))
        if resume_button.draw(screen):
            print("Переход на уровень")
        if quit_button.draw(screen):
            print("Выход из игры")
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                print("Выход из игры")

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    show_menu()
