# Importações padrão
import socket
import threading
import pickle
import struct
import time
from concurrent.futures import ThreadPoolExecutor  # ThreadPoolExecutor real!
from game_state import GameState
from settings import WIDTH, HEIGHT, BLOCK_SIZE

# Configurações do servidor
HOST = 'localhost'
PORT = 5555
MAX_PLAYERS = 4

# Dicionários para controlar conexões e dados dos jogadores
clients = {}          # { pid: conn }
player_names = {}     # { pid: "Jogador X" }
inputs = {}           # { pid: "DIREÇÃO" }
start_game_event = threading.Event()  # Sinaliza início da partida
lobby_event = threading.Event()       # Sinaliza quando o jogo está rolando
next_pid = 0                          # ID incremental dos jogadores

# Pool de threads com até 8 workers
executor = ThreadPoolExecutor(max_workers=8)

# Envia dados serializados via socket
def send_data(conn, data):
    try:
        serialized = pickle.dumps(data)
        conn.sendall(struct.pack(">I", len(serialized)) + serialized)
    except:
        pass  # Conexão quebrada, ignora

# Recebe dados serializados via socket
def recv_data(conn):
    try:
        raw_msglen = conn.recv(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack(">I", raw_msglen)[0]
        data = b""
        while len(data) < msglen:
            packet = conn.recv(msglen - len(data))
            if not packet:
                return None
            data += packet
        return pickle.loads(data)
    except:
        return None

# Envia mensagem para todos os jogadores conectados
def broadcast(msg):
    for conn in clients.values():
        send_data(conn, msg)

# Função que lida com cada jogador individualmente (usada com thread pool)
def handle_client(pid, conn):
    try:
        while True:
            data = recv_data(conn)
            if data is None:
                print(f"[x] {player_names.get(pid, 'Jogador')} desconectou.")
                break

            if data.get("type") == "start_game" and not start_game_event.is_set():
                print(f"[SERVER] {player_names.get(pid, 'Jogador')} iniciou a partida")
                start_game_event.set()

            elif data.get("type") == "input" and lobby_event.is_set():
                inputs[pid] = data.get("direction")
    finally:
        # Remove jogador ao desconectar
        if pid in clients:
            del clients[pid]
        if pid in player_names:
            del player_names[pid]
        conn.close()

# Função principal de execução do jogo (por rodada)
def game_loop():
    game = GameState(clients, player_names)

    # Inicia o jogo para todos os clientes conectados
    for pid, conn in clients.items():
        send_data(conn, {
            "type": "start",
            "player_id": pid,
            "players": player_names
        })

    time.sleep(0.5)

    # Loop do jogo em tempo real (enquanto alguém ainda estiver vivo)
    while not game.is_game_over():
        for pid, direction in inputs.items():
            game.set_input(pid, direction)

        game.update()
        state = game.get_state()
        broadcast({"type": "update", "data": state})
        time.sleep(0.15)

    # Quando o jogo termina, envia placar ajustado (desconta os 3 blocos iniciais)
    final_scores = game.get_state()["scores"]
    adjusted_scores = {pid: score - 3 for pid, score in final_scores.items()}
    broadcast({"type": "game_over", "scores": adjusted_scores})
    time.sleep(1)

# Thread em segundo plano para manter o lobby atualizando
def lobby_loop():
    while True:
        if not lobby_event.is_set():
            disconnected = []
            for pid, conn in list(clients.items()):
                try:
                    send_data(conn, {
                        "type": "lobby",
                        "connected": len(clients),
                        "max": MAX_PLAYERS
                    })
                except:
                    disconnected.append(pid)

            for pid in disconnected:
                if pid in clients:
                    del clients[pid]
                if pid in player_names:
                    del player_names[pid]
        time.sleep(1)

# Função principal do servidor
def main():
    global next_pid
    print("[*] Servidor iniciando...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    # Inicia a thread do lobby
    threading.Thread(target=lobby_loop, daemon=True).start()

    # Loop principal do servidor
    while True:
        # Reseta variáveis de controle entre partidas
        inputs.clear()
        lobby_event.clear()
        start_game_event.clear()

        # Aceita conexões até que um jogador inicie a partida
        while not start_game_event.is_set():
            server.settimeout(0.5)
            try:
                conn, addr = server.accept()

                if len(clients) >= MAX_PLAYERS:
                    send_data(conn, {"type": "full"})
                    conn.close()
                    continue

                pid = next_pid
                next_pid += 1
                clients[pid] = conn
                player_names[pid] = f"Jogador TEMP"
                print(f"[+] Conexão de {addr}")

                # Envia o cliente para uma thread do pool
                executor.submit(handle_client, pid, conn)

            except socket.timeout:
                continue

        # Renomeia os jogadores conectados (Jogador 1, 2, 3, ...)
        sorted_pids = list(clients.keys())
        player_names.clear()
        for i, pid in enumerate(sorted_pids):
            player_names[pid] = f"Jogador {i + 1}"

        print(f"[*] Iniciando partida com {len(clients)} jogadores")
        lobby_event.set()
        game_loop()
        print("[*] Partida encerrada. Retornando ao lobby...")

if __name__ == "__main__":
    main()
