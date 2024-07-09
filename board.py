import pygame
from config import Config

class Board:
    def __init__(self, screen, shop_phase):
        self.width = Config.BOARD_WIDTH
        self.height = Config.BOARD_HEIGHT
        self.shop_width = Config.SHOP_WIDTH
        self.cell_size = Config.CELL_SIZE
        self.grid_color = Config.GRID_COLOR
        self.screen = screen
        self.grid = [[0 for _ in range(self.width + self.shop_width)] for _ in range(self.height)]

        # Mark border cells as occupied
        if(shop_phase):
            for y in range(4, self.height):
                self.grid[y][self.width] = 1  # Main board right border
        
    def _mark_shop_shapes(self):
            # Example shapes in the shop area
            shapes = [
                [(self.width + 1, 4), (self.width + 2, 4), (self.width + 3, 4)],  # Shape 1
                [(self.width + 1, 6), (self.width + 2, 6), (self.width + 3, 6), (self.width + 4, 6)],  # Shape 2
                # Add more shapes as needed
            ]

            for shape in shapes:
                for (x, y) in shape:
                    self.grid[y][x] = 1  # Mark the shape itself
                    # Mark the borders around the shape
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        border_x = x + dx
                        border_y = y + dy
                        if 0 <= border_x < self.width + self.shop_width and 0 <= border_y < self.height:
                            self.grid[border_y][border_x] = 1

    def add_piece(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if piece.y + y >= 0:  # Prevent writing to negative indexes
                        self.grid[piece.y + y][piece.x + x] = 2

    def clear_lines(self, score_manager):
        lines_cleared = 0

        for y in range(self.height):
            if all(self.grid[y][x] != 0 for x in range(self.width)):  # Check only up to the main board width
                lines_cleared += 1
                # Move all rows above down by one
                for move_down_y in range(y, 0, -1):
                    for x in range(self.width):
                        self.grid[move_down_y][x] = self.grid[move_down_y - 1][x]
                # Insert a new empty row at the top
                for x in range(self.width):
                    self.grid[0][x] = 0

        # Add the cleared lines to the score manager
        if lines_cleared > 0:
            score_manager.add_lines_cleared(lines_cleared)
        
        return lines_cleared

    def can_move(self, piece, dx, dy, shop_phase):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy

                    # General boundary checks
                    if new_x < 0 or new_y >= self.height:
                        return False

                    # Check if the new position is occupied
                    if new_y >= 0 and self.grid[new_y][new_x] == 1:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x] == 2:
                        return False

                    if shop_phase:
                        if new_x >= self.width + self.shop_width - 1:
                            return False
                    else:
                        if new_x >= self.width:
                            return False

        return True

    def draw_borders(self, offset_x, offset_y, shop_phase):
        for y in range(self.height):
            if(shop_phase):
                for x in range(self.width+self.shop_width):
                    if self.grid[y][x] == 2:
                        pygame.draw.rect(self.screen, (200, 55, 169),
                                        (offset_x + x * self.cell_size,
                                        offset_y + (y-2) * self.cell_size,
                                        self.cell_size, self.cell_size))
                    if (self.grid[y][x] == 1):
                        pygame.draw.rect(self.screen, (0, 0, 0),
                                        (offset_x + x * self.cell_size,
                                        offset_y + (y-2) * self.cell_size,
                                        self.cell_size, self.cell_size))  
            else:
                for x in range(self.width):
                    if self.grid[y][x] == 2:
                        pygame.draw.rect(self.screen, (200, 55, 169),
                                        (offset_x + x * self.cell_size,
                                        offset_y + (y-2) * self.cell_size,
                                        self.cell_size, self.cell_size))
                        
    def clear_shop_area(self):
        for y in range(self.height):
            for x in range(self.width+2, self.width + self.shop_width):
                self.grid[y][x] = 0