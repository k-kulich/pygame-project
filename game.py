"""Игровой процесс."""
# 1000 и 1 импорт
import sys
import pygame
from pygame import K_DOWN, K_UP, K_LEFT, K_RIGHT, K_w, K_a, K_s, K_d
from data_loader import load_level
from my_sprites import Player, Enemy, MySprite
from bullet import Bullet
from tiles_camera import Tile, Camera
from constants import SIZE, FPS, barriers_group, player_group, enemy_group, all_sprites
from constants import bullets_group, tiles_group


pygame.init()
screen = pygame.display.set_mode(SIZE)

clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def generate_level(level):
    """Генерируем уровень. Используются следующие обозначения:
    . - просто placeholder, на его месте не создается тайла;
    e - клетка поля, на которой генерируется тайл пола и враг на нем;
    @ - клетка поля с игроком;
    w - тайл стены."""
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('floor', x, y)
            elif level[y][x] == 'w':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('floor', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'e':
                Tile('floor', x, y)
                Enemy(x, y)
    return new_player, x, y


def cut_sheet(sheet, columns, rows):
    frames = []
    rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frames.append(sheet.subsurface(pygame.Rect((rect.w * i, rect.h * j), rect.size)))
    return rect, frames


def clear_groups():
    """
    Функция для 'очистки' групп спрайтов - удаления всех существующих (из групп и в принципе).
    Для очистки поля перед загрузкой следующего уровня.
    """
    for gr in {tiles_group, barriers_group, enemy_group, player_group, bullets_group}:
        for sp in gr:
            all_sprites.remove(sp)
            gr.remove(sp)
            sp.kill()


def update_sprites(player, camera):
    """Обновление положения всех спрайтов."""
    mouse_pos = pygame.mouse.get_pos()

    # при нажатии мыши пустить пулю
    if pygame.mouse.get_pressed()[0]:
        Bullet('player', 5, *player.weapon_end, *mouse_pos)
    bullets_group.update()

    # обработать нажатие клавиш
    keys = pygame.key.get_pressed()
    new_pos = None
    if keys[K_UP] or keys[K_w]:
        new_pos = player.rect.move(0, -MySprite.SPEED)
    if keys[K_DOWN] or keys[K_s]:
        new_pos = player.rect.move(0, MySprite.SPEED)
    if keys[K_RIGHT] or keys[K_d]:
        new_pos = player.rect.move(MySprite.SPEED, 0)
    if keys[K_LEFT] or keys[K_a]:
        new_pos = player.rect.move(-MySprite.SPEED, 0)
    to_blit = player.update(new_pos, mouse_pos)

    # изменяем ракурс камеры
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)

    enemy_group.update(player.rect.center)

    # прорисовка всего, что только можно
    tiles_group.draw(screen)
    enemy_group.draw(screen)
    player_group.draw(screen)
    screen.blit(*to_blit)
    bullets_group.draw(screen)


def game():
    """
    Основной игровой цикл для уровня. Возможно в будущем изменить выбор уровня при генерации
    через вызов сторонней функции.
    """
    clear_groups()
    # TODO: заебенить отдельную функцию с циклом и гуишкой для выбора уровня
    player, *coords = generate_level(load_level('test_lvl.txt'))
    camera = Camera()
    while True:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        # обновление всего в игре вынесено в отдельную функцию
        update_sprites(player, camera)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    game()
