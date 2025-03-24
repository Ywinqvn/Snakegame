import random
from settings import WIDTH, HEIGHT, BLOCK_SIZE

# Direções possíveis baseadas no tamanho de um bloco
DIRECTIONS = {
    "UP": (0, -BLOCK_SIZE),
    "DOWN": (0, BLOCK_SIZE),
    "LEFT": (-BLOCK_SIZE, 0),
    "RIGHT": (BLOCK_SIZE, 0),
}

# Posições iniciais para até 4 jogadores
START_POSITIONS = [
    (WIDTH // 2, HEIGHT // 4),
    (3 * WIDTH // 4, HEIGHT // 2),
    (WIDTH // 2, 3 * HEIGHT // 4),
    (WIDTH // 4, HEIGHT // 2),
]

class GameState:
    def __init__(self, clients, player_names):
        self.snakes = {}          # Posição dos blocos de cada cobra
        self.directions = {}      # Direção atual de cada jogador
        self.alive = {}           # Indica se o jogador está vivo
        self.scores = {}          # Pontuação (tamanho da cobra)
        self.names = player_names
        self.players = list(clients.keys())

        # Inicializa cada cobra com 3 blocos e direção inicial "RIGHT"
        for i, pid in enumerate(self.players):
            start = START_POSITIONS[i % len(START_POSITIONS)]
            self.snakes[pid] = [
                start,
                (start[0] - BLOCK_SIZE, start[1]),
                (start[0] - 2 * BLOCK_SIZE, start[1]),
            ]
            self.directions[pid] = "RIGHT"
            self.alive[pid] = True
            self.scores[pid] = 3

        self.fruit = self.random_position()  # Gera a primeira fruta

    def random_position(self):
        # Gera uma posição aleatória válida (alinhada à grade e fora das cobras)
        cols = WIDTH // BLOCK_SIZE
        rows = HEIGHT // BLOCK_SIZE
        while True:
            x = random.randint(0, cols - 1) * BLOCK_SIZE
            y = random.randint(0, rows - 1) * BLOCK_SIZE
            pos = (x, y)
            if all(pos not in body for body in self.snakes.values()):
                return pos

    def set_input(self, pid, direction):
        # Atualiza a direção do jogador se ela não for oposta à atual
        if pid in self.directions and self.alive.get(pid):
            opposite = {
                "UP": "DOWN", "DOWN": "UP",
                "LEFT": "RIGHT", "RIGHT": "LEFT"
            }
            if direction != opposite.get(self.directions[pid]):
                self.directions[pid] = direction

    def update(self):
        new_heads = {}

        # Calcula a nova cabeça de cada cobra viva
        for pid in self.players:
            if not self.alive.get(pid):
                continue
            dx, dy = DIRECTIONS[self.directions[pid]]
            head_x, head_y = self.snakes[pid][0]
            new_head = (head_x + dx, head_y + dy)
            new_heads[pid] = new_head

        # Coleta todos os corpos (exceto cabeças)
        all_bodies = {
            pid: set(self.snakes[pid][1:]) for pid in self.players if self.alive.get(pid)
        }

        for pid, new_head in new_heads.items():
            # Verifica colisão com a parede
            out_of_bounds = (
                new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT
            )

            # Verifica colisão com corpos
            hit_body = any(new_head in body for body in all_bodies.values())

            # Verifica se duas cobras bateram cabeça com cabeça
            hit_head = list(new_heads.values()).count(new_head) > 1

            if out_of_bounds or hit_body or hit_head:
                self.alive[pid] = False  # Jogador morre
            else:
                self.snakes[pid].insert(0, new_head)  # Move cabeça

                if new_head == self.fruit:
                    self.scores[pid] += 1
                    self.fruit = self.random_position()  # Nova fruta
                else:
                    self.snakes[pid].pop()  # Remove cauda (não cresceu)

    def get_state(self):
        # Retorna todas as informações necessárias para o client desenhar o jogo
        return {
            "snakes": self.snakes,
            "fruit": self.fruit,
            "alive": self.alive,
            "scores": self.scores,
            "names": self.names
        }

    def is_game_over(self):
        # Fim do jogo quando todos os jogadores estão mortos
        return all(not self.alive.get(pid, False) for pid in self.players)
