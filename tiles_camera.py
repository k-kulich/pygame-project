"""Чисто технические объекты для загрузки уровня."""
import pygame
import random
from data_loader import load_image
from constants import tile_height, tile_width, WIDTH, HEIGHT
from constants import tiles_group, all_sprites, barriers_group


pygame.init()
pygame.display.set_mode((WIDTH, HEIGHT))


class Tile(pygame.sprite.Sprite):
    """
    Клетка поля. Класс содержит словарь с готовыми изображениями для соответствующих клеток.
    Типы: wall (стена, граница карты), table (препятствие на карте),
    floor (пустая клетка с полом).
    """
    tile_types = {'wall': pygame.Color(194, 194, 214),
                  'floor': pygame.Color(71, 71, 107),
                  'stable': load_image('table.png'),
                  'ltable': load_image('table_l.png'),
                  'mtable': load_image('table_m.png'),
                  'rtable': load_image('table_r.png'),
                  'chairs': [load_image('chair.png'), load_image('chair2.png')]}

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.type = tile_type
        self.image = self.trans_image()
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        if tile_type != 'floor':
            barriers_group.add(self)

    def trans_image(self):
        """Преобразовать изображение: развернуть столы и т.п. и вернуть итог."""
        if self.type == 'chairs':
            return random.choice(self.tile_types[self.type])
        if self.type[0] not in {'l', 'm', 'r'}:
            img = pygame.Surface((tile_width, tile_height))
            img.fill(self.tile_types[self.type])
            return img
        if 'table' in self.type:
            return self.tile_types[self.type]
        img = pygame.transform.rotate(self.tile_types[self.type[0] + 'table'], 90)
        if self.type[1] == 'r':
            return pygame.transform.flip(img, True, False)
        return img

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
    pygame.quit()
