# Arquivo: network_ws.py
# (Novo arquivo que substitui protocol.py)

import asyncio
import websockets
import threading
import json

class NetworkWS:
    def __init__(self, uri="ws://localhost:5555"):
        self.uri = uri
        self.websocket = None
        self.listener_thread = None
        self.loop = None

    def start(self, on_message_callback):
        """Inicia a conexão e o listener em uma thread separada."""
        self.listener_thread = threading.Thread(target=self._run_client, args=(on_message_callback,), daemon=True)
        self.listener_thread.start()

    def _run_client(self, on_message_callback):
        """Cria um novo loop de eventos para a thread e roda o cliente."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._client_handler(on_message_callback))

    async def _client_handler(self, on_message_callback):
        """Lida com a conexão e o recebimento de mensagens."""
        try:
            async with websockets.connect(self.uri) as websocket:
                self.websocket = websocket
                async for message in websocket:
                    on_message_callback(message)
        except Exception as e:
            print(f"Erro de conexão WebSocket: {e}")
            # Você pode chamar um callback aqui para notificar a GUI sobre a desconexão
            on_message_callback(json.dumps({"tipo": "erro", "mensagem": "Desconectado do servidor."}))


    def send(self, data_dict):
        """Envia um dicionário (JSON) para o servidor."""
        if self.websocket and self.loop:
            message = json.dumps(data_dict)
            # Envia a corotina para ser executada no loop da outra thread
            asyncio.run_coroutine_threadsafe(self.websocket.send(message), self.loop)

    def close(self):
        if self.websocket and self.loop:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)