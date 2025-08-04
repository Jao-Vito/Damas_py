import asyncio
import websockets
import json

async def terminal_client():
    """Cliente de linha de comando para interagir com o servidor de Damas."""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("--- Cliente de Terminal de Damas Conectado ---")
            print('Exemplo de jogada: {"tipo": "MOVE", "de": [5, 0], "para": [4, 1]}')

            async def receive_messages():
                """Recebe e exibe mensagens do servidor."""
                try:
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            print(f"\n<-- MENSAGEM DO SERVIDOR:\n{json.dumps(data, indent=2)}")
                            print("\n--> Digite seu comando JSON: ", end="")
                        except json.JSONDecodeError:
                            print(f"\n<-- MENSAGEM BRUTA DO SERVIDOR: {message}")
                except websockets.exceptions.ConnectionClosed:
                    print("\nConexão com o servidor foi perdida.")

            # Inicia a tarefa para receber mensagens em segundo plano
            receiver_task = asyncio.create_task(receive_messages())

            # Loop para enviar mensagens do usuário
            while True:
                try:
                    message_to_send = await asyncio.to_thread(input)
                    if message_to_send.lower() in ['exit', 'quit']:
                        break
                    
                    # Valida se o texto inserido é um JSON válido antes de enviar
                    json.loads(message_to_send) 
                    await websocket.send(message_to_send)

                except websockets.exceptions.ConnectionClosed:
                    print("\n[ERRO] Não foi possível enviar a mensagem. A conexão foi encerrada.")
                    break # Encerra o loop se a conexão for perdida
                except json.JSONDecodeError:
                    print("[ERRO] Formato JSON inválido. Tente novamente.")
                except (KeyboardInterrupt, asyncio.CancelledError):
                    break
            
            # Ao sair do loop, cancela a tarefa de recebimento
            receiver_task.cancel()
            # Aguarda a tarefa ser cancelada
            await asyncio.gather(receiver_task, return_exceptions=True)

    except ConnectionRefusedError:
        print(f"[ERRO] Não foi possível conectar ao servidor em {uri}. Verifique se o server.py está rodando.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(terminal_client())
    except KeyboardInterrupt:
        print("\nCliente de terminal encerrado.")