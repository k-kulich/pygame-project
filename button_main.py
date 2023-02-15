import pygame
import button

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

game_paused = False

font = pygame.font.SysFont("lucidaconsole", 45)

resume_b = pygame.image.load("images/resume_b.png")
quit_b = pygame.image.load("images/exit_b.png")

resume_button = button.Button(220, 230, resume_b, 1)
quit_button = button.Button(470, 230, quit_b, 1)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


run = True
while run:
    screen.fill(pygame.Color("BurlyWood"))
    if game_paused is True:
        if resume_button.draw(screen):
            game_paused = False
        if quit_button.draw(screen):
            run = False
    else:
        draw_text("Press SPACE to pause", font, "white", 130, 270)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_paused = True
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
