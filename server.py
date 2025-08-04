import asyncio
import websockets
import json
from rules import GameLogic
from board import Board

clients = []
players = {}  # Mapeia websocket -> time ("X" ou "O")
game = None

def serialize_board(board_obj):
    """Converte o objeto Board em uma lista para ser enviada via JSON."""
    serialized = []
    for row in range(8):
        serialized_row = []
        for col in range(8):
            piece = board_obj.get_piece(row, col)
            if piece == None:
                serialized_row.append(0)
            else:
                serialized_row.append({
                    "team": piece.team,
                    "king": piece.king
                })
        serialized.append(serialized_row)
    return serialized

async def broadcast_game_state():
    """Envia o estado atual do jogo (tabuleiro, turno, vencedor) para todos."""
    if not clients:
        return

    winner = game.is_winner()
    state = {
        "tipo": "fim_de_jogo" if winner else "atualizacao",
        "tabuleiro": serialize_board(game.board),
        "turno": game.turn,
        "vencedor": winner
    }
    
    message = json.dumps(state)

    tasks = [client.send(message) for client in clients]
    await asyncio.gather(*tasks)

async def handler(websocket):
    """Gerencia a conexão e as mensagens de cada cliente."""
    global game
    if len(clients) >= 2:
        await websocket.send(json.dumps({"tipo": "erro", "mensagem": "Servidor cheio."}))
        return

    clients.append(websocket)
    
    # Atribui times aos jogadores e inicia o jogo
    if len(clients) == 1:
        players[websocket] = "X" # O primeiro a conectar é "X"
        await websocket.send(json.dumps({"tipo": "info", "mensagem": "Você é o jogador X (Brancas). Aguardando oponente."}))
    elif len(clients) == 2:
        players[websocket] = "O" # O segundo a conectar é "O"
        await websocket.send(json.dumps({"tipo": "info", "mensagem": "Você é o jogador O (Pretas)."}))
        
        # Inicia o jogo
        board = Board()
        game = GameLogic(board)
        await broadcast_game_state()

    try:
        async for message in websocket:
            data = json.loads(message)
            player_team = players.get(websocket)

            # Garante que o jogo esteja em andamento e seja o turno do jogador
            if not game or player_team != game.turn:
                continue

            if data["tipo"] == "MOVE":
                de, para = tuple(data["de"]), tuple(data["para"])
                result = game.make_move(de, para)
                if result:
                    await broadcast_game_state()
            
            elif data["tipo"] == "RESET":
                board = Board()
                game = GameLogic(board)
                await broadcast_game_state()

    finally:
        clients.remove(websocket)
        if websocket in players:
            del players[websocket]
        print(f"Jogador desconectado. Clientes restantes: {len(clients)}")

async def main():
    print("Servidor de Damas (WebSocket) aguardando em ws://0.0.0.0:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())