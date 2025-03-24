import pygame
from settings import WIDTH, HEIGHT, BLOCK_SIZE, FONT, BLACK, WHITE

# Dicionário de cores fixas para os jogadores por ID
PLAYER_COLORS = {
    0: (0, 255, 0),      # Jogador 0 - Verde
    1: (0, 0, 255),      # Jogador 1 - Azul
    2: (255, 0, 0),      # Jogador 2 - Vermelho
    3: (255, 255, 0),    # Jogador 3 - Amarelo
}

# Função responsável por desenhar o estado atual do jogo na tela
def draw_game(screen, state, client_id):
    screen.fill(BLACK)  # Preenche o fundo da tela com preto

    # Desenha a fruta (rosa choque 💖)
    fruit = state["fruit"]
    pygame.draw.rect(screen, (255, 105, 180), (*fruit, BLOCK_SIZE, BLOCK_SIZE))

    # Desenha todas as cobras (uma por jogador)
    for pid, body in state["snakes"].items():
        is_alive = state["alive"].get(pid, False)  # Verifica se o jogador ainda está vivo
        color = PLAYER_COLORS.get(pid, (150, 150, 150)) if is_alive else (80, 80, 80)  # Cor viva ou morta

        # Desenha cada segmento da cobra como um quadrado
        for segment in body:
            pygame.draw.rect(screen, color, (*segment, BLOCK_SIZE, BLOCK_SIZE))

    # Mostra uma HUD com o ID do jogador local no canto da tela
    hud_text = FONT.render(f"Você é o Jogador {client_id}", True, WHITE)
    screen.blit(hud_text, (10, 10))

    # Atualiza a tela com tudo que foi desenhado
    pygame.display.flip()
