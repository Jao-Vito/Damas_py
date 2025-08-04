# Jogo de Damas - Websockets

## Autores
- João Victor, Lya Natsumi e Pedro Henrique

# 1. Instruções de Execução

Para executar o projeto, é necessário iniciar o servidor e, em seguida, conectar dois clientes. Os clientes podem ser a interface gráfica (GUI) ou o cliente de terminal.

## Passo 1: Iniciar o Servidor

O servidor é o componente central que gerencia o estado do jogo e a lógica das regras. Abra um terminal e execute:
```bash
python Damas_pitao/Damas_py/server.py
```
O servidor exibirá a mensagem "Servidor de Damas (WebSocket) aguardando em ws://0.0.0.0:8765" e ficará aguardando as conexões dos jogadores.

## Passo 2: Conectar os Jogadores (Clientes)

É preciso iniciar duas instâncias do cliente para que um jogo possa começar.

- #### Opção A: Jogar com a Interface Gráfica (GUI vs. GUI)
Abra dois novos terminais (um para cada jogador) e execute o seguinte comando em cada um deles:
```bash
# Inicia o cliente em modo remoto, conectando-se ao servidor
python Damas_pitao/Damas_py/main.py --remote
```
A primeira instância a se conectar será o Jogador "X" (Brancas), e a segunda será o Jogador "O" (Pretas).

- #### Opção B: Jogar com a Interface Gráfica vs. Terminal

No primeiro terminal, inicie a interface gráfica:

```bash
python Damas_pitao/Damas_py/main.py --remote
```
No segundo terminal, inicie o cliente de linha de comando:

```bash
python Damas_pitao/Damas_py/player.py
```

- #### Opção C: Jogar Localmente (Sem Rede)
Para jogar uma partida local, sem necessidade do servidor, execute o main.py sem argumentos:

```bash
python Damas_pitao/Damas_py/main.py
```

# 2. IPs e Portas Utilizados para Testes

Para os testes, a configuração padrão da rede é a seguinte:

- Endereço IP do Servidor: 0.0.0.0. Isso significa que o servidor escuta em todas as interfaces de rede disponíveis na máquina. Para conexões na mesma máquina, os clientes usam localhost ou 127.0.0.1. Para conexões em rede local, os clientes devem usar o IP da máquina do servidor na rede (ex: 192.168.1.10).

- Porta do Servidor: 8765.

- URI de Conexão do Cliente: Por padrão, os clientes (gui.py e player.py) tentam se conectar a ws://localhost:8765.

É possível alterar a URI de conexão do cliente gráfico através de um argumento de linha de comando:

```bash
python Damas_pitao/Damas_py/main.py --remote --uri ws://<ip_do_servidor>:8765
```

# 3. Explicação do Protocolo de Aplicação

O projeto utiliza WebSockets para comunicação em tempo real. O protocolo de aplicação define o formato das mensagens trocadas entre cliente e servidor, que são estruturadas em JSON para facilitar a leitura e o processamento. O modelo é cliente-servidor, onde o servidor é a autoridade central que valida as jogadas e distribui o estado do jogo a todos os participantes.
**Estrutura das Mensagens:**
Todas as mensagens possuem um campo "tipo" que define sua finalidade.
**A. Mensagens Enviadas pelo Cliente ao Servidor:**

1. Mover Peça (`MOVE`)
* Enviada quando um jogador realiza uma jogada.

* Exemplo:
```bash
{
  "tipo": "MOVE",
  "de": [5, 0],
  "para": [4, 1]
}
```
2. Reiniciar Jogo (`RESET`)
* Enviada pela GUI quando o botão "Reiniciar Jogo Remoto" é pressionado. O servidor reinicia o estado do jogo e notifica ambos os jogadores.

* Exemplo:
```bash
{
  "tipo": "RESET"
}
```
**B. Mensagens Enviadas pelo Servidor aos Clientes:**
1. Atualização de Estado (`atualizacao`)

* Mensagem mais comum, enviada após cada jogada válida para sincronizar o estado do jogo em todos os clientes.

* Exemplo:

```bash
{
  "tipo": "atualizacao",
  "tabuleiro": [
    [0, {"team": "O", "king": false}, 0, ...],
    [{"team": "O", "king": false}, 0, ...],
    ...,
    [0, {"team": "X", "king": false}, 0, ...],
    ...
  ],
  "turno": "O",
  "vencedor": null
}
```
* O ``tabuleiro`` é uma matriz 8x8. ``0`` representa uma casa vazia, e um objeto JSON representa uma peça.
2. Fim de Jogo (`fim_de_jogo`)
* Enviada quando a partida termina. O campo `"vencedor"` indica quem ganhou.
* Exemplo:
```bash
{
  "tipo": "fim_de_jogo",
  "tabuleiro": [...],
  "turno": "X",
  "vencedor": "X"
}
```
3. Informação (``info``)
* Usada para enviar informações gerais ao cliente, como a designação do time.
* Exemplo
```bash
{
  "tipo": "info",
  "mensagem": "Você é o jogador X (Brancas). Aguardando oponente."
}
```
4. Erro (``erro``)

* Enviada para notificar o cliente sobre um problema, como o servidor estar cheio.

* Exemplo:
```bash
{
  "tipo": "erro",
  "mensagem": "Servidor cheio."
}
```
# 4. Logs de Sessões de Teste
Abaixo estão exemplos de logs para dois cenários de teste, demonstrando o fluxo de mensagens.
**Cenário 1: Dois Jogadores com Interface Gráfica**
* **Terminal do Servidor:**

```bash
Servidor de Damas (WebSocket) aguardando em ws://0.0.0.0:8765
Jogador desconectado. Clientes restantes: 1
Jogador desconectado. Clientes restantes: 0
```

* **Ações e Mensagens (Visão Lógica):**
**1.** **Jogador 1 (GUI) conecta-se.**

* ``SERVIDOR -> JOGADOR 1``:``{"tipo": "info", "mensagem": "Você é o jogador X (Brancas). Aguardando oponente."}``

**2.** **Jogador 2 (GUI) conecta-se.**

* ``SERVIDOR -> JOGADOR 2``:``{"tipo": "info", "mensagem": "Você é o jogador O (Pretas)."}``
* ``SERVIDOR -> TODOS``:Mensagem``{"tipo": "atualizacao", ...}``  com o tabuleiro inicial e turno de "X".

**3.** **Jogador 1 (Brancas) move de [5, 2] para [4, 3].**

* ``JOGADOR 1 -> SERVIDOR``:``{"tipo": "MOVE", "de": [5, 2], "para": [4, 3]}``
* ``SERVIDOR -> TODOS``:Mensagem``{"tipo": "atualizacao", ...}``  com o tabuleiro atualizado e turno de "O".

**4.** **... a partida continua até que "X" vença.**

* ``SERVIDOR -> TODOS``:``{"tipo": "fim_de_jogo", "vencedor": "X", ...}``

**Cenário 2: Jogador 1 (GUI) vs. Jogador 2 (Terminal)**

* **Terminal do Jogador 2 (Cliente de Linha de Comando):**

```bash
--- Cliente de Terminal de Damas Conectado ---
Exemplo de jogada: {"tipo": "MOVE", "de": [5, 0], "para": [4, 1]}

<-- MENSAGEM DO SERVIDOR:
{
  "tipo": "info",
  "mensagem": "Você é o jogador O (Pretas)."
}

--> Digite seu comando JSON:
<-- MENSAGEM DO SERVIDOR:
{
  "tipo": "atualizacao",
  "tabuleiro": [...],
  "turno": "X",
  "vencedor": null
}

--> Digite seu comando JSON:
// Jogador 1 (GUI) faz uma jogada

<-- MENSAGEM DO SERVIDOR:
{
  "tipo": "atualizacao",
  "tabuleiro": [...],
  "turno": "O",
  "vencedor": null
}

--> Digite seu comando JSON: {"tipo": "MOVE", "de": [2, 1], "para": [3, 2]}

<-- MENSAGEM DO SERVIDOR:
{
  "tipo": "atualizacao",
  "tabuleiro": [...],
  "turno": "X",
  "vencedor": null
}

--> Digite seu comando JSON:
```

# 5. Atualizações no Protocolo de Aplicação
O protocolo implementado foi desenhado para ser simples e eficiente, atendendo diretamente às necessidades do jogo de Damas no modelo cliente-servidor.
Não foram necessárias extensões ou alterações complexas, pois o conjunto de mensagens definido (``MOVE``, ``RESET``, ``atualizacao``, ``info``, ``erro``, ``fim_de_jogo``) cobre todas as interações fundamentais do jogo:

* **Centralização:** O servidor mantém o estado canônico do jogo, prevenindo inconsistências.
* **Reatividade:** O uso de broadcast_game_state garante que todos os clientes recebam atualizações instantaneamente.
* **Interoperabilidade:** O formato JSON é universal e permitiu a criação de um cliente de terminal que interage com o mesmo servidor da GUI, validando a robustez do protocolo.