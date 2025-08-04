# Arquivo: player.py
# (Substitua o conteúdo do seu player.py por este)

import asyncio
import websockets
import json

async def terminal_client():
    """Cliente de linha de comando para interagir com o servidor de Damas."""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("--- Cliente de Terminal de Damas Conectado ---")
            print('Exemplo de jogada: {"tipo": "MOVE", "de": [5, 2], "para": [4, 3]}')

            async def receive_messages():
                """Recebe e exibe mensagens do servidor."""
                try:
                    async for message in websocket:
                        data = json.loads(message)
                        print(f"\n<-- MENSAGEM DO SERVIDOR:\n{json.dumps(data, indent=2)}")
                        print("\n--> Digite seu comando JSON: ", end="")
                except websockets.ConnectionClosed:
                    print("\nConexão com o servidor foi perdida.")

            receiver_task = asyncio.create_task(receive_messages())

            # Loop para enviar mensagens do usuário
            while True:
                try:
                    message_to_send = await asyncio.to_thread(input, "--> Digite seu comando JSON: ")
                    if message_to_send.lower() in ['exit', 'quit']:
                        break
                    
                    json.loads(message_to_send) # Valida o JSON
                    await websocket.send(message_to_send)
                except websockets.ConnectionClosed:
                    print("Não foi possível enviar a mensagem. Conexão encerrada.")
                    break
                except json.JSONDecodeError:
                    print("[ERRO] Formato JSON inválido. Tente novamente.")
                except (KeyboardInterrupt, asyncio.CancelledError):
                    break
            
            receiver_task.cancel()

    except ConnectionRefusedError:
        print(f"[ERRO] Não foi possível conectar ao servidor em {uri}. Verifique se o server.py está rodando.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(terminal_client())
    except KeyboardInterrupt:
        print("\nCliente de terminal encerrado.")