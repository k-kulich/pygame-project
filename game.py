"""Игровой процесс."""
# 1000 и 1 импорт
import sys
import pygame
from pygame import K_DOWN, K_UP, K_LEFT, K_RIGHT, K_w, K_a, K_s, K_d, K_e, K_SPACE
from pygame import KEYDOWN
from data_loader import load_level
from my_sprites import Player, Enemy, MySprite
from bullet import Bullet
from tiles_camera import Tile, Camera
from constants import SIZE, FPS, FRAME_H, BACK_HP, HP_H, HP_COLOR, DIFF
from constants import barriers_group, player_group, enemy_group, all_sprites, bullets_group
from constants import tiles_group
from button_main import show_menu
import mainmenu

pygame.init()
screen = pygame.display.set_mode(SIZE)

clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def create_table(tp, x, y):
    """Создать стол нужного типа. Вынесено, чтобы не засорять основную функцию."""
    table = ''
    if tp in {'⌈', '⊔', '∪'}:
        table += 'l'
    elif tp in {'-', '∃', 'E'}:
        table += 'm'
    elif tp in {'⌉', '⊓', '∩'}:
        table += 'r'
    if tp in {'t', '⌈', '-', '⌉'}:
        table += 'table'
    elif tp in '⊓∃⊔':
        table += 'r'
    else:
        table += 'l'
    Tile(table, x, y)


def generate_level(level, difficulty):
    """Генерируем уровень. Обозначения прописаны в отдельном файле."""
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            cell = level[y][x]
            if cell == '.':
                Tile('floor', x, y)
            elif cell == 'w':
                Tile('wall', x, y)
            elif cell == 'p':
                Tile('portal', x, y)
            elif cell == '@':
                Tile('floor', x, y)
                new_player = Player(x, y)
            elif cell == 'e':
                Tile('floor', x, y)
                Enemy(x, y, DIFF[difficulty])
            elif cell in {'t', '⌈', '-', '⌉', '⊓', '∃', '⊔', '∩', 'E', '∪'}:
                Tile('floor', x, y)
                create_table(cell, x, y)
            elif cell == 'c':
                Tile('floor', x, y)
                Tile('chairs', x, y)
    return new_player, x, y


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


def draw_hp_lines(player):
    """Показывает текущий уровень здоровья у игрока и злодеев."""
    pygame.draw.rect(screen, BACK_HP, pygame.Rect(10, 10, 204, FRAME_H))
    pygame.draw.rect(screen, HP_COLOR, pygame.Rect(12, 12, 200 * player.get_percent_hp(), HP_H))
    for enemy in enemy_group.sprites():
        pos = enemy.rect.left, enemy.rect.top - 5 - FRAME_H // 2
        pygame.draw.rect(screen, BACK_HP, pygame.Rect(*pos, enemy.rect.width, FRAME_H // 2))
        pygame.draw.rect(screen, HP_COLOR,
                         pygame.Rect(pos[0] + 1, pos[1] + 1,
                                     (enemy.rect.width - 2) * enemy.get_percent_hp(), HP_H // 2))


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


def level_cycle(level):
    """
    Основной игровой цикл для уровня. Возможно в будущем изменить выбор уровня при генерации
    через вызов сторонней функции.
    """
    clear_groups()

    player, *coords = generate_level(load_level(f'lvl_{level}.txt'), level)
    camera = Camera()
    pygame.display.set_caption("Main Menu")

    stop = False
    running = True
    while running:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    # Меню в середине игры
                    running, stop = show_menu()

                if event.key == K_e:
                    # если игрок нашел выход, то уровень заканчивается
                    if player.door_found:
                        stop = True
        # пока игрок не нашел выход из уровня
        if not stop:
            # обновление всего в игре вынесено в отдельную функцию
            update_sprites(player, camera)
            draw_hp_lines(player)
            # если игрок умер, то игра останавливается
            stop = not player.is_alive
        else:
            mainmenu.main_menu()

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    mainmenu.main_menu()
