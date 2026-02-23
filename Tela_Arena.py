import pygame
from ArenaObjects import Arena, Ball
from Physics2D import WorldPhysics


def _draw_text(surf, font, text, x, y, color=(235, 235, 245)):
    img = font.render(text, True, color)
    surf.blit(img, (x, y))


def TelaArena(tela, relogio, estados, config, info=None):
    W, H = tela.get_size()

    font = pygame.font.SysFont("consolas", 18)
    font_big = pygame.font.SysFont("consolas", 22, bold=True)

    arena = Arena(width=W, height=H, margin=18, wall_thick=8)

    # 2 bolas com stats próprios
    bolas = [
        Ball(x=W * 0.35, y=H * 0.55, radius=32, mass=2.6, hp=140, base_damage=1.20, color=(80, 170, 255)),
        Ball(x=W * 0.65, y=H * 0.45, radius=26, mass=1.6, hp=110, base_damage=1.50, color=(255, 120, 120)),
    ]

    physics = WorldPhysics(
        dt_fixed=1.0 / max(30, int(config.get("FPS", 120))),
        linear_damping=0.985,
        min_sleep_speed=6.0,
        restitution=0.92,
        wall_restitution=0.90,
        damage_scale=0.010,
        min_damage_impulse=80.0,
    )

    selected = 0
    aiming = False
    drag_start = (0, 0)
    last_shot_time = -999.0

    # AIM
    MAX_DRAG = 240
    AIM_POWER = 6.0
    AIM_COOLDOWN = 0.08

    SELECT_RING = (255, 235, 120)
    BG = (18, 18, 22)
    WALL = (70, 70, 85)
    AIM_LINE = (220, 220, 255)
    AIM_GHOST = (120, 120, 170)

    def inside_ball(ball, mx, my):
        return (mx - ball.x) ** 2 + (my - ball.y) ** 2 <= ball.radius ** 2

    def clamp_len(dx, dy, max_len):
        l = (dx * dx + dy * dy) ** 0.5
        if l <= 1e-9:
            return 0.0, 0.0
        if l <= max_len:
            return dx, dy
        s = max_len / l
        return dx * s, dy * s

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

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    estados["Rodando"] = False
                    rodando = False

                elif e.key == pygame.K_TAB:
                    selected = (selected + 1) % len(bolas)

                elif e.key == pygame.K_r:
                    # reset rápido
                    bolas[0].reset(W * 0.35, H * 0.55)
                    bolas[1].reset(W * 0.65, H * 0.45)

            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    b = bolas[selected]
                    if inside_ball(b, mx, my) and (tsec - last_shot_time) >= AIM_COOLDOWN and b.alive():
                        aiming = True
                        drag_start = (mx, my)

                elif e.button == 3:
                    # RMB: seleciona bola sob o mouse (ou alterna)
                    under = None
                    for i, b in enumerate(bolas):
                        if inside_ball(b, mx, my):
                            under = i
                            break
                    if under is not None:
                        selected = under
                    else:
                        selected = (selected + 1) % len(bolas)

            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1 and aiming:
                    aiming = False
                    b = bolas[selected]

                    dx = mx - drag_start[0]
                    dy = my - drag_start[1]
                    dx, dy = clamp_len(dx, dy, MAX_DRAG)

                    drag_len = (dx * dx + dy * dy) ** 0.5
                    if drag_len > 4 and b.alive():
                        # slingshot: impulso oposto ao arrasto
                        ox = -dx
                        oy = -dy
                        nlen = (ox * ox + oy * oy) ** 0.5
                        if nlen > 1e-9:
                            nx = ox / nlen
                            ny = oy / nlen
                            impulse = AIM_POWER * drag_len * b.mass
                            b.apply_impulse(nx * impulse, ny * impulse)
                            last_shot_time = tsec

        # ======================
        # UPDATE FÍSICA
        # ======================
        physics.step(arena, bolas, dt)

        # ======================
        # DRAW
        # ======================
        tela.fill(BG)

        arena.draw(tela, wall_color=WALL, bg_color=BG)

        # Aim UI
        if aiming:
            bsel = bolas[selected]
            dx = mx - drag_start[0]
            dy = my - drag_start[1]
            dx, dy = clamp_len(dx, dy, MAX_DRAG)
            ex = drag_start[0] + dx
            ey = drag_start[1] + dy

            pygame.draw.line(tela, AIM_LINE, (int(bsel.x), int(bsel.y)), (int(ex), int(ey)), 3)

            # direção prevista (oposta)
            ox = bsel.x - dx
            oy = bsel.y - dy
            pygame.draw.line(tela, AIM_GHOST, (int(bsel.x), int(bsel.y)), (int(ox), int(oy)), 2)

        # Bolas
        for i, b in enumerate(bolas):
            b.draw(tela, selected=(i == selected), ring_color=SELECT_RING)

        # HUD
        _draw_text(tela, font_big, "Controles:", 20, 16)
        _draw_text(tela, font, "LMB segurar na bola selecionada -> mirar; soltar -> lançar.", 20, 44)
        _draw_text(tela, font, "TAB troca bola | RMB seleciona/alternar | R reseta | ESC sai", 20, 64)

        y0 = 98
        for i, b in enumerate(bolas):
            tag = "BOLA 1" if i == 0 else "BOLA 2"
            sel = " (selecionada)" if i == selected else ""
            alive = "" if b.alive() else " [KO]"
            _draw_text(tela, font_big, f"{tag}{sel}{alive}", 20, y0, color=b.color)
            _draw_text(
                tela, font,
                f"HP: {b.hp:.1f}/{b.hp_max:.0f}  massa: {b.mass:.2f}  raio: {b.radius:.0f}  dano: x{b.base_damage:.2f}",
                20, y0 + 26
            )
            spd = (b.vx * b.vx + b.vy * b.vy) ** 0.5
            _draw_text(tela, font, f"vel: {spd:.1f}px/s", 20, y0 + 46)
            y0 += 84

        pygame.display.flip()

    return