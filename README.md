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
Conforme permitido pela especificação do TP3, o protocolo de aplicação base (Checkers Remote Protocol v1.0, baseado em texto plano sobre TCP) foi estendido e aprimorado para uma versão mais robusta e moderna, utilizando JSON sobre WebSockets.
As seguintes alterações foram realizadas e justificadas abaixo:
1. **Adoção de JSON em vez de Texto Plano:**

* **Justificativa:** O formato JSON é menos ambíguo e mais seguro para a troca de dados. Em vez de depender de separadores como espaços e quebras de linha (``\n``), o JSON possui uma estrutura de chave-valor que elimina erros de parsing. Além disso, é nativamente suportado pela maioria das linguagens modernas, facilitando a interoperabilidade.

2. **Estrutura de Mensagem com Campo "tipo":**

* **Justificativa:** A introdução de um campo ``"tipo"`` (ex: ``"MOVE"``, ``"atualizacao"``) torna o protocolo auto-descritivo e extensível. É possível adicionar novos tipos de mensagem no futuro sem quebrar a lógica dos clientes existentes, que podem simplesmente ignorar os tipos que não reconhecem.

3. **Sincronização de Estado Completo (``atualizacao``):**

* **Justificativa:** O protocolo base sugere que o servidor apenas ecoe a jogada (``MOVE``) para o outro cliente. Essa abordagem é frágil e pode levar a dessincronização de estado se uma mensagem for perdida. Nossa implementação envia o estado completo e oficial do tabuleiro após cada jogada. Isso garante que todos os clientes estejam sempre perfeitamente sincronizados com o servidor, que é a fonte da verdade, tornando a aplicação muito mais robusta.

4. **Inclusão de Mensagens de Feedback (``info`` e ``erro``):**

* **Justificativa:** O protocolo base não prevê mensagens de erro ou de informação. A adição desses tipos de mensagem melhora significativamente a experiência do usuário, que recebe feedback claro sobre o que está acontecendo (ex: "Servidor cheio", "Você é o jogador X"), em vez de falhas silenciosas.

Em resumo, as atualizações transformaram um protocolo simples em um sistema de comunicação completo, seguro e resiliente, aproveitando ao máximo a tecnologia de WebSockets exigida pelo TP3 e seguindo as melhores práticas de desenvolvimento de aplicações em rede.