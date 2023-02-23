"""Чисто технические объекты для загрузки уровня."""
import pygame
from constants import tile_height, tile_width, WIDTH, HEIGHT
from constants import tiles_group, all_sprites, barriers_group


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
    pygame.quit()
