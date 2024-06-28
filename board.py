import pygame
from config import Config

class Board:
    def __init__(self, screen):
        self.width = Config.BOARD_WIDTH
        self.height = Config.BOARD_HEIGHT
        self.cell_size = Config.CELL_SIZE
        self.screen = screen
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def add_piece(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if piece.y + y >= 0:  # Prevent writing to negative indexes
                        self.grid[piece.y + y][piece.x + x] = cell

    def clear_lines(self, score_manager):
        new_grid = [row for row in self.grid if not all(row)]
        lines_cleared = self.height - len(new_grid)
        new_grid = [[0 for _ in range(self.width)] for _ in range(lines_cleared)] + new_grid
        self.grid = new_grid
        
        # Add the cleared lines to the score manager
        if lines_cleared > 0:
            score_manager.add_lines_cleared(lines_cleared)
        
        return lines_cleared



    def can_move(self, piece, dx, dy):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    if new_x < 0 or new_x >= self.width or new_y >= self.height:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:  # Check only visible cells
                        return False
        return True

    def draw(self, offset_x, offset_y):
        for y in range(2, self.height):  # Skip the top 2 rows
            for x, cell in enumerate(self.grid[y]):
                if cell:
                    pygame.draw.rect(self.screen, (0, 0, 255),
                                     (offset_x + x * self.cell_size,
                                      offset_y + (y - 2) * self.cell_size,  # Adjust for hidden rows
                                      self.cell_size, self.cell_size), 0)
                    pygame.draw.rect(self.screen, (0, 0, 0),
                                     (offset_x + x * self.cell_size,
                                      offset_y + (y - 2) * self.cell_size,
                                      self.cell_size, self.cell_size), 1)
