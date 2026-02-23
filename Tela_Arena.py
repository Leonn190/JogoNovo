import pygame
from Arena import Arena
from Ball import Ball
from Physics2D import WorldPhysics


def _draw_text(surf, font, text, x, y, color=(235, 235, 245)):
    img = font.render(text, True, color)
    surf.blit(img, (x, y))


def _inside_ball(ball, mx, my):
    return (mx - ball.x) ** 2 + (my - ball.y) ** 2 <= ball.radius ** 2


def _clamp_len(dx, dy, max_len):
    l = (dx * dx + dy * dy) ** 0.5
    if l <= 1e-9:
        return 0.0, 0.0
    if l <= max_len:
        return dx, dy
    s = max_len / l
    return dx * s, dy * s


def _launch_ball(ball: Ball, drag_start, mouse_pos):
    dx = mouse_pos[0] - drag_start[0]
    dy = mouse_pos[1] - drag_start[1]
    max_drag = ball.max_drag_distance()
    dx, dy = _clamp_len(dx, dy, max_drag)

    drag_len = (dx * dx + dy * dy) ** 0.5
    if drag_len <= 4 or not ball.alive():
        return False

    ox = -dx
    oy = -dy
    nlen = (ox * ox + oy * oy) ** 0.5
    if nlen <= 1e-9:
        return False

    nx = ox / nlen
    ny = oy / nlen
    impulse = ball.launch_power(drag_len)
    ball.apply_impulse(nx * impulse, ny * impulse)
    return True


def TelaArena(tela, relogio, estados, config, info=None):
    W, H = tela.get_size()

    font = pygame.font.SysFont("consolas", 18)
    font_big = pygame.font.SysFont("consolas", 22, bold=True)

    arena = Arena(width=W, height=H, margin=18, wall_thick=8)

    bolas = [
        Ball(x=W * 0.35, y=H * 0.55, tamanho=32, peso=2.6, vida=140, dano_fisico=18, impulso=1.4, color=(80, 170, 255)),
        Ball(x=W * 0.65, y=H * 0.45, tamanho=26, peso=1.6, vida=110, dano_fisico=24, impulso=2.0, color=(255, 120, 120)),
    ]

    physics = WorldPhysics(
        dt_fixed=1.0 / max(30, int(config.get("FPS", 120))),
        linear_damping=0.985,
        min_sleep_speed=6.0,
        restitution=0.92,
        wall_restitution=0.90,
        min_damage_impulse=80.0,
        collision_damage_factor=0.02,
    )

    selected = 0
    aiming = False
    drag_start = (0, 0)
    last_shot_time = -999.0

    AIM_COOLDOWN = 0.08
    SELECT_RING = (255, 235, 120)
    BG = (18, 18, 22)
    WALL = (70, 70, 85)
    AIM_LINE = (220, 220, 255)
    AIM_GHOST = (120, 120, 170)

    rodando = True
    tsec = 0.0

    while rodando and estados.get("Rodando", True) and estados.get("Arena", False):
        dt = relogio.tick(config.get("FPS", 60)) / 1000.0
        dt = min(dt, 1 / 30)
        tsec += dt

        events = pygame.event.get()
        mx, my = pygame.mouse.get_pos()

        for e in events:
            if e.type == pygame.QUIT:
                estados["Rodando"] = False
                rodando = False

            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                estados["Rodando"] = False
                rodando = False

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, b in enumerate(bolas):
                    if _inside_ball(b, mx, my) and (tsec - last_shot_time) >= AIM_COOLDOWN and b.alive():
                        selected = i
                        aiming = True
                        drag_start = (mx, my)
                        break

            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and aiming:
                aiming = False
                b = bolas[selected]
                if _launch_ball(b, drag_start, (mx, my)):
                    last_shot_time = tsec

        physics.step(arena, bolas, dt)

        tela.fill(BG)
        arena.draw(tela, wall_color=WALL, bg_color=BG)

        if aiming:
            bsel = bolas[selected]
            dx = mx - drag_start[0]
            dy = my - drag_start[1]
            dx, dy = _clamp_len(dx, dy, bsel.max_drag_distance())
            ex = drag_start[0] + dx
            ey = drag_start[1] + dy

            pygame.draw.line(tela, AIM_LINE, (int(bsel.x), int(bsel.y)), (int(ex), int(ey)), 3)
            ox = bsel.x - dx
            oy = bsel.y - dy
            pygame.draw.line(tela, AIM_GHOST, (int(bsel.x), int(bsel.y)), (int(ox), int(oy)), 2)

        for i, b in enumerate(bolas):
            b.draw(tela, selected=(i == selected), ring_color=SELECT_RING)

        y0 = 20
        for i, b in enumerate(bolas):
            tag = f"BOLA {i + 1}"
            sel = " *" if i == selected else ""
            alive = " [KO]" if not b.alive() else ""
            _draw_text(tela, font_big, f"{tag}{sel}{alive}", 20, y0, color=b.color)
            _draw_text(
                tela,
                font,
                f"Vida {b.vida:.1f}/{b.vida_max:.0f} | DanoFis {b.dano_fisico:.1f} | Impulso {b.impulso:.2f} | Peso {b.peso:.2f} | Tam {b.tamanho:.0f}",
                20,
                y0 + 26,
            )
            _draw_text(tela, font, f"Vel {b.speed():.1f}px/s | DanoContato {b.compute_contact_damage():.1f}", 20, y0 + 46)
            y0 += 84

        pygame.display.flip()

    return
