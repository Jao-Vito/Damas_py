import asyncio
import websockets
import json

async def terminal_client():
    """Cliente de linha de comando para interagir com o servidor de Damas."""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("--- Cliente de Terminal de Damas Conectado ---")
            print("Este cliente permite enviar comandos JSON diretamente para o servidor.")
            print('Exemplo de jogada: {"tipo": "mover_peca", "de": [5, 0], "para": [4, 1]}')

            async def receive_messages():
                """Recebe e exibe mensagens do servidor."""
                try:
                    async for message in websocket:
                        data = json.loads(message)
                        print(f"\n<-- MENSAGEM DO SERVIDOR:\n{json.dumps(data, indent=2)}")
                        print("--> Digite seu comando JSON: ", end="")
                except websockets.exceptions.ConnectionClosed:
                    print("\nConexão com o servidor foi perdida.")

            receiver_task = asyncio.create_task(receive_messages())

            while not websocket.closed:
                try:
                    message_to_send = await asyncio.to_thread(input, "--> Digite seu comando JSON: ")
                    if message_to_send.lower() in ['exit', 'quit']:
                        break
                    
                    try:
                        json.loads(message_to_send)
                        await websocket.send(message_to_send)
                    except json.JSONDecodeError:
                        print("[ERRO] Formato JSON inválido. Tente novamente.")

                except (KeyboardInterrupt, asyncio.CancelledError):
                    break
            
            receiver_task.cancel()

    except ConnectionRefusedError:
        print("[ERRO] Não foi possível conectar ao servidor. Ele está rodando?")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(terminal_client())
    except KeyboardInterrupt:
        print("\nCliente de terminal encerrado.")