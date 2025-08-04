import argparse
from gui import DamasApp

if __name__ == "__main__":
    # O servidor deve ser executado em um processo separado (ex: `python server.py`).
    # Este arquivo `main.py` inicia apenas o cliente (a interface gráfica).
    
    parser = argparse.ArgumentParser(description="Cliente para o Jogo de Damas.")
    
    # Argumento para escolher entre jogo local ou remoto.
    parser.add_argument("--remote", action="store_true", 
                        help="Inicia o jogo em modo remoto, conectando a um servidor.")
    parser.add_argument("--uri", type=str, default="ws://localhost:8765", 
                        help="Endereço do servidor WebSocket (ex: ws://127.0.0.1:8765)")
    args = parser.parse_args()

    # Se a flag --remote for usada, remote_mode será True. Caso contrário, será False (jogo local).
    app = DamasApp(remote_mode=args.remote, uri=args.uri)
    app.run()