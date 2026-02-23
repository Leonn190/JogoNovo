import sys
import ctypes
import pygame

try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

pygame.init()

# ============================================================
# TELA / CLOCK
# ============================================================
tela = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Arena - Protótipo (2 bolas)")
relogio = pygame.time.Clock()

# ============================================================
# CONFIG / INFO
# ============================================================
config = {
    "FPS": 120,
}
info = {}

# ============================================================
# IMPORT DAS TELAS
# ============================================================
from Tela_Arena import TelaArena


def _estado_ativo(estados):
    for key in ("Arena",):
        if estados.get(key, False):
            return key
    return None


def _fade(tela, relogio, config, fade_in=True, dur_ms=240):
    W, H = tela.get_size()
    overlay = pygame.Surface((W, H))
    overlay.fill((0, 0, 0))

    passos = 18
    for i in range(passos + 1):
        relogio.tick(config.get("FPS", 60))
        t = i / passos
        alpha = int((1 - t) * 255) if fade_in else int(t * 255)
        overlay.set_alpha(max(0, min(255, alpha)))
        tela.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(max(1, dur_ms // passos))


# ============================================================
# ESTADOS
# ============================================================
estados = {
    "Rodando": True,
    "Arena": True,
}

# ============================================================
# LOOP PRINCIPAL
# ============================================================
ultima_tela = None
while estados["Rodando"]:
    relogio.tick(config["FPS"])

    atual = _estado_ativo(estados)
    if atual is None:
        estados["Rodando"] = False
        break

    if atual != ultima_tela:
        _fade(tela, relogio, config, fade_in=True)
        ultima_tela = atual

    if estados.get("Arena", False):
        TelaArena(tela, relogio, estados, config, info)

    proxima = _estado_ativo(estados)
    if estados.get("Rodando", False) and proxima != ultima_tela:
        _fade(tela, relogio, config, fade_in=False)
        ultima_tela = None

pygame.quit()
sys.exit()