import pygame


pygame.init()
SIZE = WIDTH, HEIGHT = 640, 640
FPS = 60

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
barriers_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()

tile_width = tile_height = 40

if __name__ == '__main__':
    pygame.quit()
