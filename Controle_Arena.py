from Ball import Ball


def criar_bolas_iniciais(largura: int, altura: int) -> list[Ball]:
    return [
        Ball(
            x=largura * 0.35,
            y=altura * 0.55,
            tamanho=32,
            peso=2.6,
            vida=140,
            dano_fisico=18,
            impulso=1.4,
            color=(80, 170, 255),
        ),
        Ball(
            x=largura * 0.65,
            y=altura * 0.45,
            tamanho=26,
            peso=1.6,
            vida=110,
            dano_fisico=24,
            impulso=2.0,
            color=(255, 120, 120),
        ),
    ]


def dentro_da_bola(bola: Ball, mx: float, my: float) -> bool:
    return (mx - bola.x) ** 2 + (my - bola.y) ** 2 <= bola.radius ** 2


def limitar_vetor(dx: float, dy: float, comprimento_maximo: float):
    comprimento = (dx * dx + dy * dy) ** 0.5
    if comprimento <= 1e-9:
        return 0.0, 0.0
    if comprimento <= comprimento_maximo:
        return dx, dy
    escala = comprimento_maximo / comprimento
    return dx * escala, dy * escala


def tentar_lancar_bola(bola: Ball, arrasto_inicio, mouse_pos) -> bool:
    dx = mouse_pos[0] - arrasto_inicio[0]
    dy = mouse_pos[1] - arrasto_inicio[1]
    dx, dy = limitar_vetor(dx, dy, bola.max_drag_distance())

    arrasto = (dx * dx + dy * dy) ** 0.5
    if arrasto <= 4 or not bola.alive():
        return False

    ox = -dx
    oy = -dy
    nlen = (ox * ox + oy * oy) ** 0.5
    if nlen <= 1e-9:
        return False

    nx = ox / nlen
    ny = oy / nlen
    impulso = bola.launch_power(arrasto)
    bola.apply_impulse(nx * impulso, ny * impulso)
    return True
