import socket                          # Para conexão com o servidor via TCP
import pygame                          # Para renderização gráfica
import threading                       # Para rodar a escuta do servidor em paralelo
import pickle                          # Para serializar objetos Python
import struct                          # Para enviar o tamanho da mensagem como cabeçalho
from settings import WIDTH, HEIGHT, FPS, WHITE, BLACK, BLOCK_SIZE

HOST = 'localhost'                    # IP do servidor (localhost para testes locais)
PORT = 5555                           # Porta do servidor

# Cores padrão dos jogadores, serão usadas conforme a ordem de conexão
PLAYER_COLORS_BASE = {
    0: (0, 255, 0),
    1: (0, 0, 255),
    2: (255, 0, 0),
    3: (255, 255, 0),
}
PLAYER_COLORS = {}  # Este dicionário será preenchido com os jogadores atuais em cada partida

# Envia um dicionário serializado para o servidor com cabeçalho de tamanho
def send_data(conn, data):
    try:
        serialized = pickle.dumps(data)                                # Serializa o objeto
        conn.sendall(struct.pack(">I", len(serialized)) + serialized)  # Envia o tamanho + dados
    except:
        pass  # Em caso de desconexão ou erro, ignora

# Recebe uma mensagem completa do servidor (respeitando o tamanho do cabeçalho)
def recv_data(conn):
    try:
        raw_msglen = conn.recv(4)  # Recebe os 4 bytes iniciais que indicam o tamanho da mensagem
        if not raw_msglen:
            return None
        msglen = struct.unpack(">I", raw_msglen)[0]
        data = b""
        while len(data) < msglen:  # Continua recebendo até ter todos os dados esperados
            packet = conn.recv(msglen - len(data))
            if not packet:
                return None
            data += packet
        return pickle.loads(data)  # Desserializa os dados recebidos
    except:
        return None

# Função para desenhar a tela do jogo em tempo real
def draw_game(screen, state, client_id, font):
    screen.fill(BLACK)  # Limpa a tela

    # Desenha a fruta
    fruit = state["fruit"]
    pygame.draw.rect(screen, (255, 105, 180), (fruit[0], fruit[1], BLOCK_SIZE, BLOCK_SIZE))

    # Desenha cada cobra
    for pid, body in state["snakes"].items():
        is_alive = state["alive"].get(pid, False)
        color = PLAYER_COLORS.get(pid, (150, 150, 150)) if is_alive else (80, 80, 80)
        for segment in body:
            pygame.draw.rect(screen, color, (*segment, BLOCK_SIZE, BLOCK_SIZE))

    # Desenha o nome do jogador local no canto superior esquerdo
    name = state["names"].get(client_id, f"Jogador {client_id}")
    color = PLAYER_COLORS.get(client_id, WHITE)
    hud = font.render(name, True, color)
    screen.blit(hud, (10, 10))

    pygame.display.flip()  # Atualiza a tela

# Mostra o placar final após o término da partida
def draw_scoreboard(screen, scores, names, font):
    screen.fill(BLACK)
    title = font.render("Placar Final", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

    # Ordena os jogadores por pontuação e mostra
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    y = 120
    for i, (pid, score) in enumerate(sorted_scores):
        name = names.get(pid, f"Jogador {pid}")
        color = PLAYER_COLORS.get(pid, WHITE)
        text = font.render(f"{name}: {score} pontos", True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
        y += 40

    pygame.display.flip()

def main():
    # Inicializa Pygame e configura a tela
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Multiplayer")
    clock = pygame.time.Clock()

    # Estabelece conexão com o servidor
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Variáveis de estado do jogo
    client_id = None
    game_running = False
    current_state = None
    connected_players = 1
    is_alive = True
    scores = None
    names = {}
    show_score = False
    score_timer = 0

    # Elementos visuais
    font = pygame.font.SysFont("arial", 28)
    button_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 10, 240, 50)
    direction = "RIGHT"

    # Thread que escuta as mensagens vindas do servidor
    def receive_thread():
        nonlocal client_id, game_running, current_state
        nonlocal connected_players, is_alive, scores, names, show_score, score_timer
        global PLAYER_COLORS

        while True:
            msg = recv_data(client)
            if msg is None:
                print("[CLIENTE] Conexão encerrada.")
                break

            # Atualiza número de jogadores no lobby
            if msg["type"] == "lobby":
                connected_players = msg.get("connected", 1)

            # Início da partida
            elif msg["type"] == "start":
                print("[CLIENTE] Partida iniciada!")
                client_id = msg["player_id"]
                names = msg.get("players", {})
                game_running = True
                is_alive = True
                scores = None
                show_score = False

                # Define as cores dos jogadores atuais
                sorted_pids = sorted(names.keys())
                PLAYER_COLORS = {
                    pid: PLAYER_COLORS_BASE[i % len(PLAYER_COLORS_BASE)]
                    for i, pid in enumerate(sorted_pids)
                }

            # Atualização do estado do jogo (posição das cobras, fruta, etc.)
            elif msg["type"] == "update":
                current_state = msg["data"]
                if not current_state["alive"].get(client_id, False):
                    is_alive = False  # O jogador morreu

            # Fim do jogo, mostra placar
            elif msg["type"] == "game_over":
                print("[CLIENTE] Partida encerrada.")
                game_running = False
                scores = msg.get("scores")
                show_score = True
                score_timer = pygame.time.get_ticks()

    # Inicia a thread de recepção de dados
    threading.Thread(target=receive_thread, daemon=True).start()

    # Loop principal do cliente
    while True:
        screen.fill(BLACK)

        # Se a partida acabou, mostrar placar por 4 segundos
        if show_score:
            draw_scoreboard(screen, scores, names, font)
            if pygame.time.get_ticks() - score_timer > 4000:
                show_score = False

        # Tela do lobby com botão "Iniciar Jogo"
        elif not game_running:
            text = font.render(f"Jogadores conectados: {connected_players}/4", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))

            mouse_pos = pygame.mouse.get_pos()
            button_hover = button_rect.collidepoint(mouse_pos)
            color = (180, 180, 180) if button_hover else (120, 120, 120)
            pygame.draw.rect(screen, color, button_rect, border_radius=8)

            button_text = font.render("Iniciar Jogo", True, BLACK)
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)

            pygame.display.flip()

        # Tela de jogo em execução
        else:
            if current_state:
                draw_game(screen, current_state, client_id, font)

        # Captura eventos de teclado e clique
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.close()
                pygame.quit()
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Clicou no botão "Iniciar Jogo"
                if not game_running and not show_score:
                    if button_rect.collidepoint(pygame.mouse.get_pos()):
                        send_data(client, {"type": "start_game"})

            elif event.type == pygame.KEYDOWN:
                # Envia direção ao servidor
                if game_running and is_alive:
                    if event.key == pygame.K_UP:
                        direction = "UP"
                    elif event.key == pygame.K_DOWN:
                        direction = "DOWN"
                    elif event.key == pygame.K_LEFT:
                        direction = "LEFT"
                    elif event.key == pygame.K_RIGHT:
                        direction = "RIGHT"
                    send_data(client, {"type": "input", "direction": direction})

        clock.tick(FPS)

if __name__ == "__main__":
    main()
