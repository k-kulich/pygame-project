"""Файл содержит все игровые классы"""
import pygame
import math
import random
from data_loader import load_image
from constants import barriers_group, player_group, enemy_group, all_sprites
from constants import WIDTH, HEIGHT, tile_height, tile_width
from bullet import Bullet


pygame.init()
pygame.display.set_mode((WIDTH, HEIGHT))


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
        self.period = random.randint(60, 150)
        self.time_gone = 0  # отсчет текущего периода
        self.maximum = random.randint(100, 200)
        self.direction = random.sample('rlud', 2)

        self.image = pygame.Surface(self.size)
        self.image.fill((0, 51, 153))
        self.rect = pygame.Rect(tile_width * (pos_x - 1), tile_height * pos_y,
                                round(tile_width * 2.5), tile_height)

    def get_hurt(self, damage):
        """
        Получить урон. В случае, если здоровье заканчивается, объект удаляется.
        :param damage: наносимый урон.
        """
        self.hp -= damage
        if self.hp < 1:
            all_sprites.remove(self)
            enemy_group.remove(self)
            self.kill()

    def shoot(self, player_center):
        if self.time_gone < self.period - 5:
            self.time_gone += 1
            return False
        self.time_gone = 0
        Bullet('enemy', 1, *self.rect.center, *player_center)

    def move(self, player_center):
        """
        Сама функция выбора новой позиции в зависимости от того, как далеко игрок.
        :param player_center: центр игрока.
        :return: rect с новой позицией.
        """
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
        """
        Обновление положения в зависимости от положения игрока.
        :param player_center: центр спрайта игрока.
        """
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
    """
    Игрок. Просто особый вид спрайта.
    """
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



if __name__ == '__main__':
    pygame.quit()
