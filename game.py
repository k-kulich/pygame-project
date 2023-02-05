import os
import sys
import pygame
import math
import random
from pygame import K_DOWN, K_UP, K_LEFT, K_RIGHT, K_w, K_a, K_s, K_d


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
    Для очистки поля перед загрузкой следующего уровня."""
    for gr in {tiles_group, barriers_group, enemy_group, player_group, bullets_group}:
        for sp in gr:
            all_sprites.remove(sp)
            gr.remove(sp)
            sp.kill()


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

        pygame.display.flip()
        clock.tick(FPS)


class MySprite(pygame.sprite.Sprite):
    """Базовый спрайт для создания игровых персонажей."""
    SPEED = 10
    PLAYER_WEAP = ['gun']
    ENEMY_WEAP = ['gun']
    weapon = {'gun': load_image('gun_small1.png', (255, 255, 255))}

    def __init__(self, pos_x, pos_y, *groups):
        super().__init__(*groups)
        self.cur_frame = 0
        self.hp = 15
        self.owned_weapon = ['gun']
        self.cur_weapon = 0
        self.direction = {'right': False, 'left': False, 'up': False, 'down': False}
        self.hurt = False
        self.weapon_end = (0, 0)
        self.rect = pygame.Rect(tile_width * pos_x, tile_height * pos_y, tile_width, tile_height)

    def handle_weapons(self):
        """
        Держать в руках изображение текущего оружия (от него зависит мощь пуль, да и просто для
        удобства игрока нужно, чтобы оружие было видно)
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()

        flipped = False  #
        # поворачиваем оружие под нужным углом
        rel_x, rel_y = mouse_x - self.rect.x, mouse_y - self.rect.y
        angle = math.degrees(-math.atan2(rel_y, rel_x))
        img = self.weapon[self.owned_weapon[self.cur_weapon]]
        if angle > 90 or angle < -90:
            img = pygame.transform.flip(img, False, True)
            flipped = True
        weapon_copy = pygame.transform.rotate(img, angle)

        # настраиваем смещение картинки, чтобы она всегда была по центру игрока
        angle = math.radians((360 + angle) % 360)
        coords = (self.rect.centerx + img.get_width() * math.cos(angle) * int(flipped),
                  self.rect.centery - img.get_height() * math.sin(angle))
        self.weapon_end = (self.rect.centerx + img.get_width() * math.cos(angle),
                           self.rect.centery - img.get_height() * math.sin(angle)
                           + tile_height * int(angle > 3.14))

        return weapon_copy, coords

    def get_weapon(self, weapon):
        self.owned_weapon.append(weapon)

    def next_weapon(self):
        self.cur_weapon = (self.cur_weapon + 1) % len(self.owned_weapon)

    def animation(self):
        pass

    def get_hurt(self, damage):
        self.hp -= damage
        # вернуть, жив ли персонаж
        return True if self.hp > 0 else False


class Enemy(MySprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, enemy_group, all_sprites)
        self.size = (round(tile_width * 2.5), round(tile_height * 1.8))
        self.period = random.randint(60, 240)
        self.time_gone = 0  # отсчет текущего периода
        self.maximum = random.randint(100, 200)
        self.direction = random.sample('rlud', 2)

        self.image = pygame.Surface(self.size)
        self.image.fill((0, 51, 153))
        self.rect = pygame.Rect(tile_width * (pos_x - 1), tile_height * pos_y,
                                round(tile_width * 2.5), tile_height)

    def get_hurt(self, damage):
        self.hp -= damage
        if self.hp < 1:
            all_sprites.remove(self)
            enemy_group.remove(self)
            self.kill()

    def shoot(self, player_center):
        if self.time_gone < self.period - 5:
            self.time_gone += 1
            return
        self.time_gone = 0
        Bullet('enemy', 1, *self.rect.center, *player_center)

    def move(self, player_center):

        # смена направления движения при необходимости
        px, py = player_center
        ex, ey = self.rect.centerx, self.rect.centery
        ob = ''
        if (px - ex) ** 2 + (py - ey) ** 2 >= self.maximum ** 2:
            if (px - ex) ** 2 > (py - ey) ** 2:
                ob = 'l' if px < ex else 'r'
            else:
                ob = 'u' if py < ey else 'd'
        if ob and ob in 'lr':
            self.direction = ob + random.choice('ud' + ob)
        elif ob:
            self.direction = ob + random.choice('lr' + ob)

        # движение согласно текущему направлению
        coor_delta = [0, 0]
        if 'l' in self.direction:
            coor_delta[0] -= self.SPEED
        elif 'r' in self.direction:
            coor_delta[0] += self.SPEED
        if 'u' in self.direction:
            coor_delta[1] -= self.SPEED
        elif 'd' in self.direction:
            coor_delta[1] += self.SPEED

        return self.rect.move(*coor_delta)

    def update(self, player_center):
        # смена направления движения
        new_pos = self.move(player_center)
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
        # стрелять по игроку
        self.shoot(player_center)


class Player(MySprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, player_group, all_sprites)
        self.hp = 100
        self.size = (tile_width, round(tile_height * 1.8))
        self.delta_h = self.size[1] - tile_width
        self.image = pygame.Surface(self.size)
        self.image.fill((204, 0, 0))
        self.current_weapon = 'gun'

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
    """Пуля. Все ее характеристики, а также разница, выпущена ли игроком или в игрока."""
    SPEED = 15
    SIZE = (5, 5)

    def __init__(self, owner, damage, x, y, mouse_x, mouse_y):
        super().__init__(bullets_group, all_sprites)
        self.owner = owner
        self.damage = damage
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

        # при столкновении со стеной пуля исчезает
        if pygame.sprite.spritecollideany(self, barriers_group):
            bullets_group.remove(self)
            self.kill()

        # если пуля выпущена игроком, то она не приносит ему урона, иначе наоборот
        gr = enemy_group if self.owner == 'player' else player_group
        c = 0
        for c, sp in enumerate(pygame.sprite.spritecollide(self, gr, dokill=False), 1):
            sp.get_hurt(self.damage)
            if isinstance(sp, Player):
                print(sp.hp)
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
