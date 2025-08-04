from piece import Piece

class Board:
    def __init__(self):
        self.size = 8
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.initialize_pieces()

    def initialize_pieces(self):
        for row in range(3):
            for col in range(self.size):
                if (row + col) % 2 == 1:
                    self.grid[row][col] = Piece("O", row, col)
        for row in range(5, 8):
            for col in range(self.size):
                if (row + col) % 2 == 1:
                    self.grid[row][col] = Piece("X", row, col)

    def move_piece(self, from_pos, to_pos):
        piece = self.grid[from_pos[0]][from_pos[1]]
        self.grid[to_pos[0]][to_pos[1]] = piece
        self.grid[from_pos[0]][from_pos[1]] = None
        piece.row, piece.col = to_pos
        # Verifica promoção
        if (piece.team == "X" and to_pos[0] == 0) or (piece.team == "O" and to_pos[0] == 7):
            piece.promote()

    def get_piece(self, row, col):
        return self.grid[row][col]

    def remove_piece(self, row, col):
        self.grid[row][col] = None
