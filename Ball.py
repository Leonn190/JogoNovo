import math
import pygame


class Ball:
    def __init__(
        self,
        x,
        y,
        tamanho,
        peso,
        vida,
        dano_fisico,
        impulso,
        color,
    ):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

        self.tamanho = float(tamanho)
        self.peso = float(peso)
        self.inv_mass = 0.0 if self.peso <= 0 else 1.0 / self.peso

        self.vida_max = float(vida)
        self.vida = float(vida)

        self.dano_fisico = float(dano_fisico)
        self.impulso = float(impulso)
        self.color = color

        self.hit_flash = 0.0

    @property
    def radius(self):
        return self.tamanho

    @property
    def mass(self):
        return self.peso

    @property
    def hp(self):
        return self.vida

    @property
    def hp_max(self):
        return self.vida_max

    def alive(self) -> bool:
        return self.vida > 0.0

    def reset_motion(self):
        self.vx = 0.0
        self.vy = 0.0

    def reset(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.reset_motion()
        self.vida = self.vida_max
        self.hit_flash = 0.0

    def speed(self):
        return math.hypot(self.vx, self.vy)

    def launch_power(self, drag_len: float):
        return drag_len * self.impulso * self.peso

    def max_drag_distance(self):
        return 80.0 + self.impulso * 45.0

    def compute_contact_damage(self):
        velocidade = self.speed()
        return (self.dano_fisico * 0.5) + (velocidade * 0.25) + (self.peso * 0.25)

    def apply_impulse(self, ix, iy):
        self.vx += ix * self.inv_mass
        self.vy += iy * self.inv_mass

    def take_damage(self, dmg):
        if dmg <= 0:
            return
        self.vida = max(0.0, self.vida - float(dmg))
        self.hit_flash = 0.10

    def draw(self, surf, selected=False, ring_color=(255, 235, 120)):
        if self.hit_flash > 0:
            t = self.hit_flash / 0.10
            glow = int(110 * t)
            c = (
                min(255, self.color[0] + glow),
                min(255, self.color[1] + glow),
                min(255, self.color[2] + glow),
            )
        else:
            c = self.color

        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), int(self.tamanho))

        if selected:
            pygame.draw.circle(surf, ring_color, (int(self.x), int(self.y)), int(self.tamanho + 6), 3)

        bar_w = int(self.tamanho * 2.2)
        bar_h = 8
        bx = int(self.x - bar_w / 2)
        by = int(self.y - self.tamanho - 18)

        pygame.draw.rect(surf, (40, 40, 50), (bx, by, bar_w, bar_h), border_radius=4)
        frac = 0.0 if self.vida_max <= 0 else self.vida / self.vida_max
        fill = int(bar_w * frac)

        col = (90, 220, 120) if frac > 0.6 else (255, 210, 90) if frac > 0.3 else (255, 90, 90)
        pygame.draw.rect(surf, col, (bx, by, fill, bar_h), border_radius=4)
        pygame.draw.rect(surf, (0, 0, 0), (bx, by, bar_w, bar_h), 1, border_radius=4)
