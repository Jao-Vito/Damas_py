import argparse
from Damas_py.gui import DamasApp
from Damas_py.network_ws import NetworkHandler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", action="store_true", help="Inicia como servidor")
    parser.add_argument("--client", action="store_true", help="Inicia como cliente")
    parser.add_argument("--host", type=str, default="localhost", help="Endereço do host")
    parser.add_argument("--port", type=int, default=5555, help="Porta de conexão")
    args = parser.parse_args()

    # Define modo de rede (se aplicável)
    if args.server or args.client:
        is_server = args.server
        network = NetworkHandler(is_server=is_server, host=args.host, port=args.port)
        network.start()
        app = DamasApp(network=network, remote_mode=True)
    else:
        app = DamasApp()

    app.run()