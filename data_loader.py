"""Функции, подгружающие данные из внешних файлов."""
import os
import sys
import pygame


pygame.init()


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    """Функция для загрузки уровня из текстового файла."""
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


def load_image(name, colorkey=None):
    """Функция для загрузки и преобразования изображения."""
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


pygame.quit()
