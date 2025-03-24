# Importa a biblioteca pickle para serializar/deserializar objetos Python
import pickle

# Importa a biblioteca struct para empacotar/desempacotar dados binários
import struct

# Função para enviar dados de forma segura com cabeçalho de tamanho
def send_data(conn, data):
    try:
        # Serializa o objeto Python (dict, lista, etc.) em bytes
        serialized = pickle.dumps(data)

        # struct.pack(">I", len(serialized)) cria um cabeçalho de 4 bytes
        # representando o tamanho da mensagem (big-endian, inteiro sem sinal)
        header = struct.pack(">I", len(serialized))

        # Envia o cabeçalho seguido dos dados serializados
        conn.sendall(header + serialized)

    except:
        # Se ocorrer qualquer erro (como desconexão), ignora
        pass
# Função para receber dados enviados com cabeçalho de tamanho
def recv_data(conn):
    try:
        # Primeiro, tenta ler os 4 bytes iniciais do cabeçalho
        raw_msglen = conn.recv(4)

        # Se não receber nada, a conexão foi encerrada ou inválida
        if not raw_msglen:
            return None

        # Interpreta os 4 bytes como um inteiro (tamanho da mensagem)
        msglen = struct.unpack(">I", raw_msglen)[0]

        # Prepara buffer para armazenar os dados recebidos
        data = b""

        # Continua recebendo até alcançar o tamanho total da mensagem
        while len(data) < msglen:
            packet = conn.recv(msglen - len(data))  # Recebe o restante
            if not packet:
                return None  # Se não receber, algo deu errado
            data += packet  # Adiciona ao buffer

        # Desserializa os dados de volta para objeto Python original
        return pickle.loads(data)

    except:
        # Se falhar em qualquer etapa, retorna None
        return None