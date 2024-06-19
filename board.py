import pygame

class Board:
    def __init__(self, screen):
        self.width = 10
        self.height = 20
        self.cell_size = 18 # Idk which cell_size takes priority
        self.screen = screen
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def add_piece(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[piece.y + y][piece.x + x] = cell

    def clear_lines(self):
        new_grid = [row for row in self.grid if not all(row)]
        lines_cleared = self.height - len(new_grid)
        new_grid = [[0 for _ in range(self.width)] for _ in range(lines_cleared)] + new_grid
        self.grid = new_grid
        return lines_cleared

    def can_move(self, piece, dx, dy):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                        return False
                    if self.grid[new_y][new_x]:
                        return False
        return True

    def draw(self, offset_x, offset_y):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, (0, 0, 255),
                                     (offset_x + x * self.cell_size,
                                      offset_y + y * self.cell_size,
                                      self.cell_size, self.cell_size), 0)
                    pygame.draw.rect(self.screen, (0, 0, 0),
                                     (offset_x + x * self.cell_size,
                                      offset_y + y * self.cell_size,
                                      self.cell_size, self.cell_size), 1)
