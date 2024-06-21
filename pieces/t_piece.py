import pygame
from config import Config
import wallkicks

class TPiece:
    def __init__(self):
        self.states = [
            [[0, 1, 0],
             [1, 1, 1],
             [0, 0, 0]],
             
            [[0, 1, 0],
             [0, 1, 1],
             [0, 1, 0]],
             
            [[0, 0, 0],
             [1, 1, 1],
             [0, 1, 0]],
             
            [[0, 1, 0],
             [1, 1, 0],
             [0, 1, 0]]
        ]
        self.current_state = 0
        self.shape = self.states[self.current_state]
        self.x = 4
        self.y = 2
        self.cell_size = Config.CELL_SIZE
        self.color = (160, 32, 240)  # PURPLE
        self.type = 'T'

    def rotate(self, reverse=False, board=None):
        initial_state = self.current_state
        if reverse:
            self.current_state = (self.current_state - 1) % len(self.states)
        else:
            self.current_state = (self.current_state + 1) % len(self.states)
        self.shape = self.states[self.current_state]

        if board:
            kicks = wallkicks.get_wall_kicks(self.type, initial_state, self.current_state)
            for x_offset, y_offset in kicks:
                if board.can_move(self, x_offset, y_offset):
                    self.x += x_offset
                    self.y += y_offset
                    return
            # If no valid kicks, revert to original state
            self.current_state = initial_state
            self.shape = self.states[self.current_state]

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
        copied_piece = TPiece()
        copied_piece.states = [state[:] for state in self.states]
        copied_piece.current_state = self.current_state
        copied_piece.shape = self.shape[:]
        copied_piece.x = self.x
        copied_piece.y = self.y
        copied_piece.color = self.color
        copied_piece.type = self.type
        return copied_piece
