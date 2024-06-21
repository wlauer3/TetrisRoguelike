import pygame
from config import Config


class OPiece:
    def __init__(self):
        self.states = [
            [[1, 1],
             [ 1, 1]],
             
        ]
        self.current_state = 0
        self.shape = self.states[self.current_state]
        self.x = 4
        self.y = 1
        self.cell_size = Config.CELL_SIZE
        self.color = (255,255,0)  # YELLOW
    
    def rotate(self):
        pass  # O piece does not rotate

    def draw(self, screen, offset_x, offset_y):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.color,
                                     (offset_x + (self.x + x) * self.cell_size,
                                      offset_y + (self.y + y) * self.cell_size,
                                      self.cell_size, self.cell_size), 0)
                    pygame.draw.rect(screen, (0, 0, 0),
                                     (offset_x + (self.x + x) * self.cell_size,
                                      offset_y + (self.y + y) * self.cell_size,
                                      self.cell_size, self.cell_size), 1)
    def copy(self):
        copied_piece = OPiece()
        copied_piece.states = [state[:] for state in self.states]
        copied_piece.current_state = self.current_state
        copied_piece.shape = self.shape[:]
        copied_piece.x = self.x
        copied_piece.y = self.y
        return copied_piece