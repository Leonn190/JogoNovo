import pygame


class Arena:
    def __init__(self, width: int, height: int, margin: int = 18, wall_thick: int = 8):
        self.width = int(width)
        self.height = int(height)
        self.margin = int(margin)
        self.wall_thick = int(wall_thick)

    def outer_rect(self) -> pygame.Rect:
        return pygame.Rect(self.margin, self.margin, self.width - 2 * self.margin, self.height - 2 * self.margin)

    def inner_rect(self) -> pygame.Rect:
        r = self.outer_rect()
        return r.inflate(-2 * self.wall_thick, -2 * self.wall_thick)

    def bounds_for_circle(self, radius: float):
        inner = self.inner_rect()
        left = inner.left + radius
        right = inner.right - radius
        top = inner.top + radius
        bottom = inner.bottom - radius
        return left, right, top, bottom

    def draw(self, surf, wall_color=(70, 70, 85), bg_color=(18, 18, 22)):
        outer = self.outer_rect()
        inner = self.inner_rect()
        pygame.draw.rect(surf, wall_color, outer, border_radius=14)
        pygame.draw.rect(surf, bg_color, inner, border_radius=12)


class Ball:
    def __init__(self, x, y, radius, mass, hp, base_damage, color):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

        self.radius = float(radius)
        self.mass = float(mass)
        self.inv_mass = 0.0 if self.mass <= 0 else 1.0 / self.mass

        self.hp_max = float(hp)
        self.hp = float(hp)

        self.base_damage = float(base_damage)
        self.color = color

        self.hit_flash = 0.0

    def alive(self) -> bool:
        return self.hp > 0.0

    def reset(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.hp = self.hp_max
        self.hit_flash = 0.0

    def apply_impulse(self, ix, iy):
        # impulso altera velocidade por impulso/massa
        self.vx += ix * self.inv_mass
        self.vy += iy * self.inv_mass

    def take_damage(self, dmg):
        if dmg <= 0:
            return
        self.hp = max(0.0, self.hp - float(dmg))
        self.hit_flash = 0.10

    def draw(self, surf, selected=False, ring_color=(255, 235, 120)):
        # hit flash simples
        if self.hit_flash > 0:
            t = self.hit_flash / 0.10
            glow = int(110 * t)
            c = (min(255, self.color[0] + glow),
                 min(255, self.color[1] + glow),
                 min(255, self.color[2] + glow))
        else:
            c = self.color

        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), int(self.radius))

        if selected:
            pygame.draw.circle(surf, ring_color, (int(self.x), int(self.y)), int(self.radius + 6), 3)

        # barra HP
        bar_w = int(self.radius * 2.2)
        bar_h = 8
        bx = int(self.x - bar_w / 2)
        by = int(self.y - self.radius - 18)

        pygame.draw.rect(surf, (40, 40, 50), (bx, by, bar_w, bar_h), border_radius=4)
        frac = 0.0 if self.hp_max <= 0 else self.hp / self.hp_max
        fill = int(bar_w * frac)

        col = (90, 220, 120) if frac > 0.6 else (255, 210, 90) if frac > 0.3 else (255, 90, 90)
        pygame.draw.rect(surf, col, (bx, by, fill, bar_h), border_radius=4)
        pygame.draw.rect(surf, (0, 0, 0), (bx, by, bar_w, bar_h), 1, border_radius=4)