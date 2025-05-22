class GameLogic:
    def __init__(self, board):
        self.board = board
        self.turn = "X"

    def is_opponent(self, piece):
        return piece and piece.team != self.turn

    def valid_moves(self, piece):
        moves, captures = [], []
        directions = []

        if piece.king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            directions = [(-1, -1), (-1, 1)] if piece.team == "X" else [(1, -1), (1, 1)]

        for dr, dc in directions:
            r, c = piece.row + dr, piece.col + dc
            
            if not piece.king:
                # Movimento normal das peças (não-dama), igual seu código atual
                if 0 <= r < 8 and 0 <= c < 8:
                    if self.board.get_piece(r, c) is None:
                        moves.append((r, c))
                    elif self.is_opponent(self.board.get_piece(r, c)):
                        jump_r, jump_c = r + dr, c + dc
                        if 0 <= jump_r < 8 and 0 <= jump_c < 8 and self.board.get_piece(jump_r, jump_c) is None:
                            captures.append((jump_r, jump_c))
            else:
                # Movimento da dama: percorrer a diagonal até encontrar peça ou limite
                step = 1
                while True:
                    rr = piece.row + dr * step
                    cc = piece.col + dc * step
                    if not (0 <= rr < 8 and 0 <= cc < 8):
                        break  # saiu do tabuleiro

                    current_piece = self.board.get_piece(rr, cc)

                    if current_piece is None:
                        # casa vazia -> pode mover aqui
                        moves.append((rr, cc))
                        step += 1
                    else:
                        # achou uma peça
                        if self.is_opponent(current_piece):
                            # Verifica se pode pular (capturar)
                            jump_r = rr + dr
                            jump_c = cc + dc
                            if 0 <= jump_r < 8 and 0 <= jump_c < 8 and self.board.get_piece(jump_r, jump_c) is None:
                                captures.append((jump_r, jump_c))
                        # independente de capturar ou não, não pode pular outra peça na mesma direção
                        break

        return captures + moves


    def make_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board.get_piece(from_row, from_col)
        if not piece or piece.team != self.turn:
            return False

        valid = self.valid_moves(piece)
        if to_pos not in valid:
            return False

        # Se for captura, remover peça capturada
        if abs(to_row - from_row) == 2:
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            self.board.remove_piece(mid_row, mid_col)

        self.board.move_piece(from_pos, to_pos)

        # Checar promoção
        if piece.team == "X" and to_row == 0:
            piece.promote()
        elif piece.team == "O" and to_row == 7:
            piece.promote()

        # Verificar captura múltipla
        if abs(to_row - from_row) == 2:
            new_captures = [move for move in self.valid_moves(piece) if abs(move[0] - to_row) == 2]
            if new_captures:
                return "again"  # indicar ao UI que o jogador pode capturar novamente

        self.turn = "O" if self.turn == "X" else "X"
        return True

    def is_winner(self):
        x_pieces = []
        o_pieces = []
        
        # Separar as peças de cada time
        for row in self.board.grid:
            for piece in row:
                if piece:
                    if piece.team == "X":
                        x_pieces.append(piece)
                    else:
                        o_pieces.append(piece)
        
        # Se algum time não tiver peças, o outro venceu
        if not x_pieces:
            return "O"
        if not o_pieces:
            return "X"
        
        # Função auxiliar para checar se um time tem pelo menos um movimento válido
        def tem_movimento_valido(pecas):
            for p in pecas:
                if self.valid_moves(p):
                    return True
            return False
        
        # Se um time não tiver movimentos válidos, perdeu
        if not tem_movimento_valido(x_pieces):
            return "O"
        if not tem_movimento_valido(o_pieces):
            return "X"
        
        # Caso contrário, ninguém venceu ainda
        return None

