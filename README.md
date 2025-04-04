# 🐍 Snake Multiplayer - Jogo em Rede com Sockets TCP

Um jogo multiplayer simples do clássico **Snake**, implementado em **Python**, utilizando **sockets TCP** com uma arquitetura **cliente-servidor**. Cada jogador controla sua cobra em tempo real, competindo pela fruta em um ambiente sincronizado pelo servidor central.

---

## 🚀 Tecnologias Utilizadas

- Python 3
- Sockets TCP
- `ThreadPoolExecutor` (Thread pool para conexões simultâneas)
- `pygame` (interface gráfica)
- Threads (`threading`)
- Comunicação binária com `pickle` + `struct`

---

## 🎮 Como Funciona

- O servidor aceita até **4 jogadores simultâneos**
- Cada jogador é nomeado automaticamente (Jogador 1, 2, etc.)
- As cobras recebem cores únicas e reiniciam a cada partida
- A colisão entre cobras é detectada corretamente
- Jogadores eliminados se tornam espectadores até o fim da rodada
- Todos voltam ao lobby para uma nova partida ao final

---

## 🖥️ Executando o Projeto

### Pré-requisitos:
- Python 3.10+
- pygame (`pip install pygame`)

### Rodando o servidor:
```bash
python server.py
```

### Rodando os clientes:
Em terminais separados (até 4):
```bash
python client.py
```

💡 Para testes em rede local:  
- No `client.py`, altere a linha `HOST = 'localhost'` para o IP local da máquina onde o servidor está rodando 

---

## 🔃 Comunicação Cliente-Servidor

- O cliente envia:
  - Direções (`"UP"`, `"DOWN"`, etc.)
  - Pedido para iniciar o jogo
- O servidor envia:
  - Estado do jogo em tempo real
  - Mensagens de lobby, início e fim de partida
  - Pontuação final dos jogadores

---

## 🔐 Gerenciamento de Conexões

- O servidor usa `ThreadPoolExecutor` para gerenciar os jogadores
- Conexões acima do limite são rejeitadas com aviso
- Desconexões são detectadas automaticamente e removidas do lobby

---

## 🧪 Testes Realizados

- ✅ 1 a 4 jogadores simultâneos
- ✅ Detecção de colisão entre cobras e paredes
- ✅ Jogadores mortos se tornam espectadores
- ✅ Reinício automático para o lobby após a partida
- ✅ Comunicação testada entre 2 computadores via rede local
- ✅ Reconexão e reinício sem reiniciar o servidor

---

## 📄 Estrutura do Projeto

```
snake2/
│
├── server.py          # Lógica principal do servidor
├── client.py          # Interface do cliente (com pygame)
├── game_state.py      # Lógica e estado do jogo
├── settings.py        # Configurações globais
├── utils.py           # Envio e recebimento de dados via socket
└── README.md          # Você está aqui 😉
```


## 🏁 Licença

Esse projeto é livre para uso acadêmico e aprendizado. Use como base para estudos e outros jogos em rede! 🎓
