import pygame


pygame.init()
SIZE = WIDTH, HEIGHT = 640, 640
FPS = 60

COLLIDE_DAMAGE = 1

BACK_HP = pygame.Color(224, 224, 235, 50)
HP_COLOR = pygame.Color(179, 0, 0, 70)
FRAME_H = 24
HP_H = 20

DIFF = {1: 'light', 2: 'normal', 3: 'normal', 4: 'hard', 5: 'hard', 6: 'little boss'}

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
barriers_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()

tile_width = tile_height = 40

if __name__ == '__main__':
    pygame.quit()
