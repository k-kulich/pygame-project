import os
import sys
import pygame
import math
from pygame import K_DOWN, K_UP, K_LEFT, K_RIGHT


pygame.init()
SIZE = WIDTH, HEIGHT = 640, 640
FPS = 60
screen = pygame.display.set_mode(SIZE)

clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
barriers_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()

tile_width = tile_height = 40


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден", file=sys.stderr)
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename

    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
    except Exception:
        print(f"Файл '{filename}' не найден", file=sys.stderr)
        terminate()

    max_width = max(map(len, level_map))
    # дополнить строку слева символами 'n'
    return list(map(lambda x: x.ljust(max_width, 'n'), level_map))


def generate_level(level):
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
    return new_player, x, y


def cut_sheet(sheet, columns, rows):
    frames = []
    rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frames.append(sheet.subsurface(pygame.Rect((rect.w * i, rect.h * j), rect.size)))
    return rect, frames


def game():
    player, *coords = generate_level(load_level('test_lvl.txt'))
    camera = Camera()
    while True:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        mouse_pos = pygame.mouse.get_pos()

        if pygame.mouse.get_pressed()[0]:
            Bullet('player', player.rect.centerx, player.rect.centery + tile_height, *mouse_pos)
        bullets_group.update()

        # обработать нажатие клавиш
        keys = pygame.key.get_pressed()
        new_pos = None
        if keys[K_UP]:
            new_pos = player.rect.move(0, -MySprite.SPEED)
        if keys[K_DOWN]:
            new_pos = player.rect.move(0, MySprite.SPEED)
        if keys[K_RIGHT]:
            new_pos = player.rect.move(MySprite.SPEED, 0)
        if keys[K_LEFT]:
            new_pos = player.rect.move(-MySprite.SPEED, 0)
        to_blit = player.update(new_pos, mouse_pos)

        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        tiles_group.draw(screen)
        enemy_group.draw(screen)
        player_group.draw(screen)
        screen.blit(*to_blit)
        bullets_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


class MySprite(pygame.sprite.Sprite):
    SPEED = 10

    def __init__(self, pos_x, pos_y, *groups):
        super().__init__(*groups)
        self.cur_frame = 0
        self.rect = pygame.Rect(tile_width * pos_x, tile_height * pos_y, tile_width, tile_height)

    def get_hurt(self):
        pass


class Enemy(MySprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, enemy_group, all_sprites)


class Player(MySprite):
    weapons = {'gun': load_image('gun_small1.png', (255, 255, 255))}

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, player_group, all_sprites)
        self.size = (tile_width, round(tile_height * 1.8))
        self.delta_h = self.size[1] - tile_width
        self.image = pygame.Surface(self.size)
        self.image.fill((204, 0, 0))
        self.current_weapon = 'gun'

    def handle_weapons(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - (self.rect.centery + tile_height)
        angle = math.degrees(-math.atan2(rel_y, rel_x))
        img = self.weapons[self.current_weapon]
        if angle > 90 or angle < -90:
            img = pygame.transform.flip(img, False, True)
        player_weapon_copy = pygame.transform.rotate(img, angle)

        return player_weapon_copy, (self.rect.centerx,
                                    self.rect.y + tile_height)

    def update(self, new_pos, mouse_pos):
        if new_pos is None:
            return self.handle_weapons()
        # проверка, занята ли новая позиция препятствием
        new_pos.y += tile_height
        last_pos = self.rect
        self.rect = new_pos
        if pygame.sprite.spritecollideany(self, barriers_group):
            self.rect = last_pos
            return self.handle_weapons()
        self.rect.y -= tile_height
        return self.handle_weapons()


class Bullet(pygame.sprite.Sprite):
    SPEED = 15
    SIZE = (5, 5)

    def __init__(self, owner, x, y, mouse_x, mouse_y):
        super().__init__(bullets_group, all_sprites)
        self.owner = owner
        self.angle = math.atan2(y - mouse_y, x - mouse_x)
        self.x_vel = math.cos(self.angle) * Bullet.SPEED
        self.y_vel = math.sin(self.angle) * Bullet.SPEED

        self.image = pygame.Surface(self.SIZE)
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x -= int(self.x_vel)
        self.rect.y -= int(self.y_vel)

        if pygame.sprite.spritecollideany(self, barriers_group):
            bullets_group.remove(self)
            self.kill()

        gr = enemy_group if self.owner == 'player' else player_group
        c = 0
        for c, sp in enumerate(pygame.sprite.spritecollide(self, gr, dokill=False), 1):
            sp.get_hurt()
        if c > 0:
            bullets_group.remove(self)
            self.kill()


class Tile(pygame.sprite.Sprite):
    """
    Клетка поля. Класс содержит словарь с готовыми изображениями для соответствующих клеток.
    Типы: wall (стена, граница карты), table (препятствие на карте),
    floor (пустая клетка с полом).
    """
    tile_types = {'wall': pygame.Color(45, 45, 134),
                  'floor': pygame.Color(198, 198, 235),
                  'table': pygame.Color(51, 102, 153)}

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = pygame.Surface((tile_width, tile_height))
        self.image.fill(self.tile_types[tile_type])
        self.type = tile_type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        if tile_type in {'wall', 'table'}:
            barriers_group.add(self)

    def tile_type(self):
        return self.type


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.updated = False

    def apply(self, obj):
        """Сдвинуть объект obj на смещение камеры."""
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        self.updated = False

    def update(self, target):
        """Установить смещение камеры по положению объекта target."""
        if target is None:
            return
        self.dx = -(target.rect.x + 10 - WIDTH // 2)
        self.dy = -(target.rect.y + 20 - HEIGHT // 2)
        self.updated = True


if __name__ == '__main__':
    game()
