import tkinter as tk
from tkinter import messagebox
from board.board import Board
from game_logic.rules import GameLogic

class DamasApp:
    def __init__(self, network=None, remote_mode=False):
        self.window = tk.Tk()
        self.window.title("Jogo de Damas")
        self.canvas = tk.Canvas(self.window, width=640, height=640)
        self.canvas.pack()
        self.board = Board()
        self.logic = GameLogic(self.board)
        self.turn_label = tk.Label(self.window, text=f"Turno: {self.logic.turn}", font=("Arial", 16))
        self.turn_label.pack()
        self.selected = None
        self.remote_mode = remote_mode
        self.network = network

        # Botões
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack()
        self.local_button = tk.Button(self.button_frame, text="Novo Jogo Local", command=self.reset_local)
        self.local_button.pack(side=tk.LEFT)
        self.remote_button = tk.Button(self.button_frame, text="Reiniciar Jogo Remoto", command=self.reset_remote)
        self.remote_button.pack(side=tk.LEFT)

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

        if self.remote_mode and self.network:
            self.network.start_listener(self.on_message)

    def draw_board(self):
        self.canvas.delete("all")
        color1, color2 = "#DDB88C", "#A66D4F"
        for row in range(8):
            for col in range(8):
                x1, y1 = col * 80, row * 80
                x2, y2 = x1 + 80, y1 + 80
                color = color1 if (row + col) % 2 == 0 else color2
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                piece = self.board.get_piece(row, col)
                if piece:
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10,
                                            fill="white" if piece.team == "X" else "black")
                    if piece.king:
                        self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text="K",
                                                fill="red", font=("Arial", 20, "bold"))
        
        if self.selected:
            piece = self.board.get_piece(*self.selected)
            if piece and piece.team == self.logic.turn:
                valid_moves = self.logic.valid_moves(piece)
                for (r, c) in valid_moves:
                    x1, y1 = c * 80, r * 80
                    x2, y2 = x1 + 80, y1 + 80
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)
        self.turn_label.config(text=f"Turno: {self.logic.turn}")


    def on_click(self, event):
        if self.remote_mode and self.logic.turn != ("X" if self.network.is_server else "O"):
            return  # Aguarda a jogada do oponente

        col, row = event.x // 80, event.y // 80
        if self.selected:
            result = self.logic.make_move(self.selected, (row, col))
            if result:
                if self.remote_mode and self.network:
                    self.network.send(f"MOVE {self.selected[0]},{self.selected[1]} {row},{col}")

                if result == "again":
                    self.selected = (row, col)
                else:
                    self.selected = None

                winner = self.logic.is_winner()
                if winner:
                    messagebox.showinfo("Fim de jogo", f"Vitória de {winner}")
                    if self.remote_mode:
                        self.network.send(f"WIN {winner}")
            else:
                self.selected = None  # movimento inválido cancela seleção

            self.draw_board()
        elif self.board.get_piece(row, col):
            piece = self.board.get_piece(row, col)
            if piece.team == self.logic.turn:
                self.selected = (row, col)
                self.draw_board()

    def on_message(self, msg):
        parts = msg.strip().split()
        if parts[0] == "MOVE" and len(parts) == 3:
            try:
                from_row, from_col = map(int, parts[1].split(','))
                to_row, to_col = map(int, parts[2].split(','))
                self.logic.make_move((from_row, from_col), (to_row, to_col))
                self.draw_board()
            except:
                print("Erro ao processar mensagem MOVE.")
        elif parts[0] == "WIN" and len(parts) == 2:
            messagebox.showinfo("Fim de jogo", f"Vitória de {parts[1]}")
        elif parts[0] == "RESET":
            self.reset_local()

    def reset_local(self):
        self.board = Board()
        self.logic = GameLogic(self.board)
        self.selected = None
        self.draw_board()

    def reset_remote(self):
        self.reset_local()
        if self.remote_mode and self.network:
            self.network.send("RESET")

    def run(self):
        self.window.mainloop()
