class Piece:
    def __init__(self, team, row, col):
        self.team = team
        self.row = row
        self.col = col
        self.king = False

    def promote(self):
        self.king = True

    def symbol(self):
        return self.team.upper() if self.king else self.team