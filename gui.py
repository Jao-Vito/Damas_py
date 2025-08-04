# Arquivo: gui.py
# (Substitua o conteúdo do seu gui.py por este)

import tkinter as tk
from tkinter import messagebox
import json
from board import Board
from rules import GameLogic
from network_ws import NetworkWS # Importa o novo handler de rede

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
        self.player_team = None # "X" ou "O"

        if self.remote_mode:
            self.network = NetworkWS(uri)
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
        # ... (seu método draw_board não precisa de alterações)
        self.canvas.delete("all")
        color1, color2 = "#DDB88C", "#A66D4F"
        for row in range(8):
            for col in range(8):
                x1, y1 = col * 80, row * 80
                x2, y2 = x1 + 80, y1 + 80
                color = color1 if (row + col) % 2 == 0 else color2
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                piece = self.logic.board.get_piece(row, col)
                if piece:
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10,
                                            fill="white" if piece.team == "X" else "black")
                    if piece.king:
                        self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text="K",
                                                fill="red", font=("Arial", 20, "bold"))
        
        if self.selected:
            piece = self.logic.board.get_piece(*self.selected)
            if piece and piece.team == self.logic.turn:
                valid_moves = self.logic.valid_moves(piece)
                for (r, c) in valid_moves:
                    x1, y1 = c * 80, r * 80
                    x2, y2 = x1 + 80, y1 + 80
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)
        self.turn_label.config(text=f"Turno: {self.logic.turn}")


    def on_click(self, event):
        # Em modo remoto, só permite clicar se for o turno do jogador
        if self.remote_mode and self.logic.turn != self.player_team:
            return

        col, row = event.x // 80, event.y // 80
        if self.selected:
            result = self.logic.make_move(self.selected, (row, col))
            if result:
                if self.remote_mode:
                    # Envia a jogada para o servidor no formato JSON
                    self.network.send({"tipo": "MOVE", "de": self.selected, "para": (row, col)})

                if result == "again":
                    self.selected = (row, col)
                else:
                    self.selected = None
            else:
                self.selected = None  # movimento inválido cancela seleção
            
            # A atualização do tabuleiro agora é recebida do servidor
            if not self.remote_mode:
                self.check_winner_and_draw()
        elif self.logic.board.get_piece(row, col):
            piece = self.logic.board.get_piece(row, col)
            if piece.team == self.logic.turn:
                self.selected = (row, col)
                self.draw_board()

    def on_message(self, msg):
        """Processa mensagens JSON recebidas do servidor."""
        try:
            data = json.loads(msg)
            
            # Define o time do jogador com base na primeira mensagem do servidor
            if data.get("tipo") == "info" and "Você é o jogador" in data.get("mensagem", ""):
                self.player_team = "X" if "X (Brancas)" in data["mensagem"] else "O"
                self.window.title(f"Damas Online - Você é {self.player_team}")

            # Se for uma atualização de jogo ou fim de jogo, reconstrói o tabuleiro
            elif data.get("tipo") in ["atualizacao", "fim_de_jogo"]:
                # --- LÓGICA DE ATUALIZAÇÃO CORRIGIDA ---
                
                # 1. Atualiza o turno
                self.logic.turn = data["turno"]

                # 2. Reconstrói o tabuleiro do zero com os dados do servidor
                from piece import Piece # Importa a classe Piece
                new_board = Board()
                new_board.grid = [[None for _ in range(8)] for _ in range(8)]
                for r, row_data in enumerate(data["tabuleiro"]):
                    for c, piece_data in enumerate(row_data):
                        if piece_data != 0:
                            p = Piece(piece_data["team"], r, c)
                            if piece_data["king"]:
                                p.promote()
                            new_board.grid[r][c] = p
                
                # 3. Substitui o tabuleiro antigo pelo novo
                self.logic.board = new_board
                
                # 4. Redesenha a tela com o novo estado
                self.draw_board()

                # 5. Se o jogo acabou, mostra a mensagem
                if data.get("tipo") == "fim_de_jogo" and data.get("vencedor"):
                    messagebox.showinfo("Fim de Jogo", f"Vitória de {data['vencedor']}!")

            elif data.get("tipo") == "erro":
                messagebox.showerror("Erro do Servidor", data["mensagem"])

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao processar mensagem do servidor: {msg} | {e}")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao processar mensagem do servidor: {msg} | {e}")

    def update_game_state(self, state):
        """Atualiza o tabuleiro e o turno com base nos dados do servidor."""
        # Recria o tabuleiro a partir dos dados recebidos
        new_board = Board()
        new_board.grid = [[None for _ in range(8)] for _ in range(8)]
        for r, row_data in enumerate(state["tabuleiro"]):
            for c, piece_data in enumerate(row_data):
                if piece_data != 0:
                    piece = self.logic.board.get_piece(r, c) # Reutiliza a peça para manter o objeto
                    if piece:
                       piece.team = piece_data["team"]
                       piece.king = piece_data["king"]
                       new_board.grid[r][c] = piece
                    else:
                        from piece import Piece
                        p = Piece(piece_data["team"], r, c)
                        p.king = piece_data["king"]
                        new_board.grid[r][c] = p


        self.logic.board = new_board
        self.logic.turn = state["turno"]
        self.draw_board()

    def check_winner_and_draw(self):
        winner = self.logic.is_winner()
        if winner:
            messagebox.showinfo("Fim de Jogo", f"Vitória de {winner}!")
        self.draw_board()

    def reset_local(self):
        self.logic = GameLogic(Board())
        self.selected = None
        self.draw_board()

    def reset_remote(self):
        if self.remote_mode and self.network:
            self.network.send({"tipo": "RESET"})

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    # Para jogar localmente
    # app = DamasApp(remote_mode=False)
    
    # Para jogar remotamente (inicie duas instâncias)
    app = DamasApp(remote_mode=True, uri="ws://localhost:8765") # Mude o IP se necessário
    
    app.run()