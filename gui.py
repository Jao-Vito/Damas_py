import tkinter as tk
from tkinter import messagebox
import json
from board import Board
from rules import GameLogic
from network_ws import NetworkWS # Importa o novo handler de rede
from piece import Piece

class DamasApp:
    def __init__(self, remote_mode=False, uri="ws://localhost:8765"):
        self.window = tk.Tk()
        self.window.title("Jogo de Damas")
        self.canvas = tk.Canvas(self.window, width=640, height=640)
        self.canvas.pack()
        self.logic = GameLogic(Board())
        self.turn_label = tk.Label(self.window, text=f"Turno: {self.logic.turn}", font=("Arial", 16))
        self.turn_label.pack()
        self.selected = None
        
        self.remote_mode = remote_mode
        self.network = None
        self.player_team = None # Será "X" ou "O"

        if self.remote_mode:
            self.network = NetworkWS(uri)
            # A função on_message será o callback para o handler de rede
            self.network.start(self.on_message)

        # Botões
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack()
        self.local_button = tk.Button(self.button_frame, text="Novo Jogo Local", command=self.reset_local)
        self.local_button.pack(side=tk.LEFT)
        self.remote_button = tk.Button(self.button_frame, text="Reiniciar Jogo Remoto", command=self.reset_remote)
        self.remote_button.pack(side=tk.LEFT)

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        """Desenha o tabuleiro e as peças com base no estado atual de self.logic.board."""
        self.canvas.delete("all")
        color1, color2 = "#DDB88C", "#A66D4F" # Cores padrão
        for row in range(8):
            for col in range(8):
                x1, y1 = col * 80, row * 80
                x2, y2 = x1 + 80, y1 + 80
                color = color1 if (row + col) % 2 == 0 else color2
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                piece = self.logic.board.get_piece(row, col)
                if piece:
                    fill_color = "white" if piece.team == "X" else "black"
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill=fill_color)
                    if piece.king:
                        self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text="K", fill="red", font=("Arial", 20, "bold"))
        
        # Destaca movimentos válidos para a peça selecionada
        if self.selected:
            piece = self.logic.board.get_piece(*self.selected)
            if piece:
                valid_moves = self.logic.valid_moves(piece)
                for (r, c) in valid_moves:
                    x1, y1 = c * 80, r * 80
                    x2, y2 = x1 + 80, y1 + 80
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)
        
        self.turn_label.config(text=f"Turno: {self.logic.turn}")

    def on_click(self, event):
        """Processa o clique do mouse para selecionar ou mover uma peça."""
        col, row = event.x // 80, event.y // 80

        # Em modo remoto, impede o jogador de jogar fora do seu turno
        if self.remote_mode and (not self.player_team or self.logic.turn != self.player_team):
            return

        if self.selected:
            from_pos = self.selected
            to_pos = (row, col)
            self.selected = None # Deseleciona a peça após a tentativa

            if self.remote_mode:
                # No modo remoto, apenas envia a jogada ao servidor. Não altera o estado local.
                self.network.send({"tipo": "MOVE", "de": from_pos, "para": to_pos})
            else:
                # No modo local, a lógica do jogo é executada diretamente.
                result = self.logic.make_move(from_pos, to_pos)
                if result == "again": # Captura múltipla
                    self.selected = to_pos
                self.check_winner_and_draw() # Atualiza o tabuleiro localmente
        else:
            # Tenta selecionar uma peça
            piece = self.logic.board.get_piece(row, col)
            if piece and piece.team == self.logic.turn:
                self.selected = (row, col)
                self.draw_board() # Redesenha para mostrar os movimentos possíveis

    def on_message(self, msg):
        """Processa mensagens JSON recebidas do servidor (executado na thread de rede)."""
        try:
            data = json.loads(msg)
            
            if data.get("tipo") == "info" and "Você é o jogador" in data.get("mensagem", ""):
                self.player_team = "X" if "X (Brancas)" in data["mensagem"] else "O"
                self.window.title(f"Damas Online - Você é {self.player_team}")

            elif data.get("tipo") in ["atualizacao", "fim_de_jogo"]:
                # Atualiza o turno
                self.logic.turn = data["turno"]

                # Reconstrói o tabuleiro com os dados do servidor
                new_board = Board()
                new_board.grid = [[None for _ in range(8)] for _ in range(8)]
                for r, row_data in enumerate(data["tabuleiro"]):
                    for c, piece_data in enumerate(row_data):
                        if piece_data != 0:
                            p = Piece(piece_data["team"], r, c)
                            if piece_data.get("king", False):
                                p.promote()
                            new_board.grid[r][c] = p
                
                self.logic.board = new_board
                self.draw_board()

                if data.get("tipo") == "fim_de_jogo" and data.get("vencedor"):
                    # Usa `after` para garantir que a messagebox seja executada na thread principal da GUI
                    self.window.after(100, lambda: messagebox.showinfo("Fim de Jogo", f"Vitória de {data['vencedor']}!"))

            elif data.get("tipo") == "erro":
                messagebox.showerror("Erro do Servidor", data["mensagem"])

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao processar mensagem do servidor: {msg} | {e}")

    def check_winner_and_draw(self):
        """Verifica se há um vencedor e atualiza o tabuleiro (usado no modo local)."""
        winner = self.logic.is_winner()
        if winner:
            messagebox.showinfo("Fim de Jogo", f"Vitória de {winner}!")
        self.draw_board()

    def reset_local(self):
        """Reinicia um novo jogo no modo local."""
        self.remote_mode = False
        self.player_team = None
        self.logic = GameLogic(Board())
        self.selected = None
        self.window.title("Jogo de Damas")
        self.draw_board()

    def reset_remote(self):
        """Envia um pedido ao servidor para reiniciar o jogo remoto."""
        if self.remote_mode and self.network:
            self.network.send({"tipo": "RESET"})

    def run(self):
        """Inicia o loop principal da aplicação."""
        self.window.mainloop()