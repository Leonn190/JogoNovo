import pygame


class Arena:
    def __init__(
        self,
        width: int,
        height: int,
        margin: int = 18,
        wall_thick: int = 8,
        wall_radius: int = 14,
        floor_radius: int = 12,
    ):
        self.width = int(width)
        self.height = int(height)
        self.margin = int(margin)
        self.wall_thick = int(wall_thick)
        self.wall_radius = int(wall_radius)
        self.floor_radius = int(floor_radius)

    def resize(self, width: int, height: int):
        self.width = int(width)
        self.height = int(height)

    def outer_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.margin,
            self.margin,
            self.width - 2 * self.margin,
            self.height - 2 * self.margin,
        )

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

    def contains_point(self, x: float, y: float) -> bool:
        return self.inner_rect().collidepoint(int(x), int(y))

    def clamp_circle_position(self, x: float, y: float, radius: float):
        left, right, top, bottom = self.bounds_for_circle(radius)
        return (
            min(max(x, left), right),
            min(max(y, top), bottom),
        )

    def draw(self, surf, wall_color=(70, 70, 85), bg_color=(18, 18, 22)):
        outer = self.outer_rect()
        inner = self.inner_rect()
        pygame.draw.rect(surf, wall_color, outer, border_radius=self.wall_radius)
        pygame.draw.rect(surf, bg_color, inner, border_radius=self.floor_radius)
