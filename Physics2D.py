import math
from ArenaObjects import Arena, Ball


class WorldPhysics:
    def __init__(
        self,
        dt_fixed=1 / 120,
        linear_damping=0.985,
        min_sleep_speed=6.0,
        restitution=0.92,
        wall_restitution=0.90,
        damage_scale=0.010,
        min_damage_impulse=80.0,
    ):
        self.dt_fixed = float(dt_fixed)
        self.linear_damping = float(linear_damping)
        self.min_sleep_speed = float(min_sleep_speed)
        self.restitution = float(restitution)
        self.wall_restitution = float(wall_restitution)

        self.damage_scale = float(damage_scale)
        self.min_damage_impulse = float(min_damage_impulse)

        self._accum = 0.0

    def step(self, arena: Arena, balls: list[Ball], dt: float):
        # acumula e roda passos fixos (física consistente)
        self._accum += float(dt)
        max_steps = 6
        steps = 0

        while self._accum >= self.dt_fixed and steps < max_steps:
            self._accum -= self.dt_fixed
            self._step_fixed(arena, balls, self.dt_fixed)
            steps += 1

        # se travar/fps cair, não deixa acumular infinito
        self._accum = min(self._accum, self.dt_fixed)

    def _step_fixed(self, arena: Arena, balls: list[Ball], dt: float):
        # integra
        for b in balls:
            self._integrate(b, dt)
            self._resolve_wall(arena, b)

        # colisões bola-bola (por enquanto 2 bolas, mas funciona para N)
        n = len(balls)
        for i in range(n):
            for j in range(i + 1, n):
                impulse_mag, hitter, target = self._resolve_ball_ball(balls[i], balls[j])
                if impulse_mag > 0 and hitter is not None and target is not None:
                    self._apply_damage(impulse_mag, hitter, target)

        # reduz hit flash
        for b in balls:
            if b.hit_flash > 0:
                b.hit_flash = max(0.0, b.hit_flash - dt)

    def _integrate(self, b: Ball, dt: float):
        if not b.alive():
            b.vx *= 0.92
            b.vy *= 0.92

        b.x += b.vx * dt
        b.y += b.vy * dt

        b.vx *= self.linear_damping
        b.vy *= self.linear_damping

        if math.hypot(b.vx, b.vy) < self.min_sleep_speed:
            b.vx = 0.0
            b.vy = 0.0

    def _resolve_wall(self, arena: Arena, b: Ball):
        left, right, top, bottom = arena.bounds_for_circle(b.radius)

        if b.x < left:
            b.x = left
            b.vx = -b.vx * self.wall_restitution
        elif b.x > right:
            b.x = right
            b.vx = -b.vx * self.wall_restitution

        if b.y < top:
            b.y = top
            b.vy = -b.vy * self.wall_restitution
        elif b.y > bottom:
            b.y = bottom
            b.vy = -b.vy * self.wall_restitution

    def _resolve_ball_ball(self, a: Ball, b: Ball):
        dx = b.x - a.x
        dy = b.y - a.y
        dist = math.hypot(dx, dy)
        min_dist = a.radius + b.radius

        if dist <= 1e-9:
            dist = 1e-6
            dx, dy = 1.0, 0.0

        if dist >= min_dist:
            return 0.0, None, None

        nx = dx / dist
        ny = dy / dist

        # correção posicional (separação) proporcional à inv_mass
        penetration = (min_dist - dist)
        inv_mass_sum = a.inv_mass + b.inv_mass
        if inv_mass_sum > 0:
            corr = penetration / inv_mass_sum
            a.x -= nx * corr * a.inv_mass
            a.y -= ny * corr * a.inv_mass
            b.x += nx * corr * b.inv_mass
            b.y += ny * corr * b.inv_mass

        # velocidade relativa
        rvx = b.vx - a.vx
        rvy = b.vy - a.vy
        vel_along_n = rvx * nx + rvy * ny

        # se já está separando, não aplica impulso
        if vel_along_n > 0:
            return 0.0, None, None

        # impulso (colisão elástica com restituição)
        j = -(1 + self.restitution) * vel_along_n
        inv_mass_sum = a.inv_mass + b.inv_mass
        if inv_mass_sum <= 0:
            return 0.0, None, None
        j /= inv_mass_sum

        ix = j * nx
        iy = j * ny

        a.vx -= ix * a.inv_mass
        a.vy -= iy * a.inv_mass
        b.vx += ix * b.inv_mass
        b.vy += iy * b.inv_mass

        # decide "hitter" vs "target" pelo quanto cada um estava empurrando na normal
        a_to_b = a.vx * nx + a.vy * ny       # positivo em direção a b
        b_to_a = -(b.vx * nx + b.vy * ny)    # positivo em direção a a

        if a_to_b > b_to_a:
            return abs(j), a, b
        elif b_to_a > a_to_b:
            return abs(j), b, a
        else:
            # empate: sem hitter claro (pode ignorar dano aqui)
            return abs(j), None, None

    def _apply_damage(self, impulse_mag: float, hitter: Ball, target: Ball):
        if impulse_mag < self.min_damage_impulse:
            return
        dmg = impulse_mag * self.damage_scale * hitter.base_damage
        target.take_damage(dmg)