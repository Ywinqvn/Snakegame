from utils import send_data, recv_data  # Funções utilitárias para comunicação via socket

# Função que gerencia a comunicação com um jogador individual
# conn: conexão com o cliente
# addr: endereço do cliente (IP e porta)
# pid: ID do jogador
# lobby_event: evento que indica quando o jogo começa
# input_queue: fila compartilhada para enviar inputs ao servidor
# disconnect_event: evento para indicar que o jogador foi desconectado
def handle_player(conn, addr, pid, lobby_event, input_queue, disconnect_event):
    print(f"[+] Jogador {pid} conectado: {addr}")  # Log de conexão

    try:
        # Envia mensagem inicial de lobby ao cliente
        send_data(conn, {"type": "lobby", "msg": "Aguardando outros jogadores..."})

        # Aguarda todos os jogadores entrarem e o lobby liberar
        lobby_event.wait()

        # Loop principal do jogador (enquanto ele estiver conectado)
        while not disconnect_event.is_set():
            data = recv_data(conn)  # Recebe input do jogador

            if not data:
                break  # Conexão encerrada

            # Se o tipo de dado for input, adiciona à fila
            if data.get("type") == "input":
                input_queue.put((pid, data["direction"]))

    except:
        print(f"[x] Jogador {pid} desconectou")  # Log de erro ou desconexão forçada

    finally:
        disconnect_event.set()  # Marca esse jogador como desconectado
        conn.close()            # Fecha a conexão com o cliente
