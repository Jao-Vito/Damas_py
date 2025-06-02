class GameLogic:
    def __init__(self, board):
        self.board = board
        self.turn = "X"

    def is_opponent(self, piece):
        return piece and piece.team != self.turn

    def forced_captures(self):
        captures = []
        for row in self.board.grid:
            for piece in row:
                if piece and piece.team == self.turn:
                    piece_captures = self._calculate_piece_captures(piece)
                    captures.extend((piece.row, piece.col, r, c) for (r, c) in piece_captures)
        return captures

    def _calculate_piece_captures(self, piece):
        captures = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if piece.king else (
            [(-1, -1), (-1, 1)] if piece.team == "X" else [(1, -1), (1, 1)]
        )

        for dr, dc in directions:
            if piece.king:
                found_opponent = False
                for step in range(1, 8):
                    r, c = piece.row + dr * step, piece.col + dc * step
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    
                    target = self.board.get_piece(r, c)
                    if target:
                        if self.is_opponent(target) and not found_opponent:
                            found_opponent = True
                            jump_r, jump_c = r + dr, c + dc
                            if (0 <= jump_r < 8 and 0 <= jump_c < 8 and 
                                self.board.get_piece(jump_r, jump_c) is None):
                                captures.append((jump_r, jump_c))
                        else:
                            break 
            else:
                # Regular piece capture
                r, c = piece.row + dr, piece.col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = self.board.get_piece(r, c)
                    if target and self.is_opponent(target):
                        jump_r, jump_c = r + dr, c + dc
                        if (0 <= jump_r < 8 and 0 <= jump_c < 8 and 
                            self.board.get_piece(jump_r, jump_c) is None):
                            captures.append((jump_r, jump_c))
        return captures

    def valid_moves(self, piece, force=True):
        moves = []
        captures = self._calculate_piece_captures(piece)  # Use helper method
        
        # Only calculate normal moves if no forced captures exist
        if not force or not self.forced_captures():
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if piece.king else (
                [(-1, -1), (-1, 1)] if piece.team == "X" else [(1, -1), (1, 1)]
            )
            
            for dr, dc in directions:
                if piece.king:
                    # King movement
                    for step in range(1, 8):
                        r, c = piece.row + dr * step, piece.col + dc * step
                        if not (0 <= r < 8 and 0 <= c < 8) or self.board.get_piece(r, c):
                            break
                        moves.append((r, c))
                else:
                    # Regular movement
                    r, c = piece.row + dr, piece.col + dc
                    if 0 <= r < 8 and 0 <= c < 8 and self.board.get_piece(r, c) is None:
                        moves.append((r, c))
        
        return captures if force and self.forced_captures() else captures + moves

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