import pygame
from Arena import Arena
from Physics2D import WorldPhysics
from Controle_Arena import criar_bolas_iniciais, dentro_da_bola, limitar_vetor, tentar_lancar_bola


COR_FUNDO = (18, 18, 22)
COR_PAREDE = (70, 70, 85)
COR_SELECAO = (255, 235, 120)
COR_LINHA_MIRA = (220, 220, 255)
COR_FANTASMA_MIRA = (120, 120, 170)
ESPERA_ENTRE_DISPAROS = 0.08


def TelaArena(tela, relogio, estados, config, info=None):
    largura, altura = tela.get_size()

    arena = Arena(width=largura, height=altura, margin=18, wall_thick=8)
    bolas = criar_bolas_iniciais(largura, altura)

    fisica = WorldPhysics(
        dt_fixed=1.0 / max(30, int(config.get("FPS", 120))),
        linear_damping=0.985,
        min_sleep_speed=6.0,
        restitution=0.92,
        wall_restitution=0.90,
        min_damage_impulse=80.0,
        collision_damage_factor=0.02,
    )

    indice_selecionado = 0
    mirando = False
    inicio_arrasto = (0, 0)
    ultimo_disparo = -999.0

    rodando = True
    tempo_total = 0.0

    while rodando and estados.get("Rodando", True) and estados.get("Arena", False):
        dt = relogio.tick(config.get("FPS", 60)) / 1000.0
        dt = min(dt, 1 / 30)
        tempo_total += dt

        eventos = pygame.event.get()
        mx, my = pygame.mouse.get_pos()

        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Rodando"] = False
                rodando = False

            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                estados["Rodando"] = False
                rodando = False

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for i, bola in enumerate(bolas):
                    if dentro_da_bola(bola, mx, my) and (tempo_total - ultimo_disparo) >= ESPERA_ENTRE_DISPAROS and bola.alive():
                        indice_selecionado = i
                        mirando = True
                        inicio_arrasto = (mx, my)
                        break

            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1 and mirando:
                mirando = False
                bola = bolas[indice_selecionado]
                if tentar_lancar_bola(bola, inicio_arrasto, (mx, my)):
                    ultimo_disparo = tempo_total

        fisica.step(arena, bolas, dt)

        tela.fill(COR_FUNDO)
        arena.draw(tela, wall_color=COR_PAREDE, bg_color=COR_FUNDO)

        if mirando:
            bola = bolas[indice_selecionado]
            dx = mx - inicio_arrasto[0]
            dy = my - inicio_arrasto[1]
            dx, dy = limitar_vetor(dx, dy, bola.max_drag_distance())
            final_x = inicio_arrasto[0] + dx
            final_y = inicio_arrasto[1] + dy

            pygame.draw.line(tela, COR_LINHA_MIRA, (int(bola.x), int(bola.y)), (int(final_x), int(final_y)), 3)
            oposto_x = bola.x - dx
            oposto_y = bola.y - dy
            pygame.draw.line(tela, COR_FANTASMA_MIRA, (int(bola.x), int(bola.y)), (int(oposto_x), int(oposto_y)), 2)

        for i, bola in enumerate(bolas):
            bola.draw(tela, selected=(i == indice_selecionado), ring_color=COR_SELECAO)

        pygame.display.flip()
