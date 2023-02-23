"""Исключительно класс пули."""
import math
import pygame
from constants import bullets_group, all_sprites, barriers_group, player_group, enemy_group


pygame.init()


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
        if c > 0:
            bullets_group.remove(self)
            self.kill()

if __name__ == '__main__':
    pygame.quit()
