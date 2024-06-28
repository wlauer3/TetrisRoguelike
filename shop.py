# shop.py
import random
import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_DOWN, K_UP, K_SPACE, K_c

class Shop:
    def __init__(self, screen, screen_width, screen_height, main_board):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.main_board = main_board
        self.title_font = pygame.font.Font(None, 48)
        self.box_font = pygame.font.Font(None, 36)

        self.slots = self.generate_slots()
        self.selected_piece = None  # Track the piece being moved

    def generate_slots(self):
        # Generate a random Tetris piece in state 0 (initial orientation)
        shapes = [
            [(0, 0), (1, 0), (2, 0)],  # I shape (horizontal)
            [(0, 0), (1, 0), (0, 1)],  # L shape
            [(0, 0), (1, 0), (1, 1)],  # S shape
        ]
        shape = random.choice(shapes)

        # Label the slots
        labels = ["Hold Piece", "Queue", "Crab"]

        # Position the slots to the left of the main board
        slot_positions = []
        for i, (x, y) in enumerate(shape):
            slot_x = self.main_board.offset_x // 2 - self.main_board.cell_size
            slot_y = self.main_board.offset_y + y * self.main_board.cell_size + i * 40
            slot_positions.append((slot_x, slot_y, labels[i]))

        return slot_positions

    def draw_main_board(self):
        for y in range(self.main_board.height):
            for x, cell in enumerate(self.main_board.grid[y]):
                if cell:
                    pygame.draw.rect(self.screen, (128, 128, 128),
                                     (self.main_board.offset_x + x * self.main_board.cell_size,
                                      self.main_board.offset_y + (y-2) * self.main_board.cell_size,
                                      self.main_board.cell_size, self.main_board.cell_size))

    def draw_shop(self):
        # Draw the main game board in the middle
        self.draw_main_board()

        # Draw the title on the left
        title_text = "Shop"
        title = self.title_font.render(title_text, True, (0, 0, 0))
        title_rect = title.get_rect(center=(self.main_board.offset_x // 2, self.main_board.offset_y // 2))
        self.screen.blit(title, title_rect)

        # Draw the slots
        for slot_x, slot_y, label in self.slots:
            pygame.draw.rect(self.screen, (0, 0, 0), (slot_x, slot_y, self.main_board.cell_size, self.main_board.cell_size), 2)
            label_text = self.box_font.render(label, True, (0, 0, 0))
            label_rect = label_text.get_rect(center=(slot_x + self.main_board.cell_size // 2, slot_y - 20))
            self.screen.blit(label_text, label_rect)

        # Draw the labels inside the slots
        for slot_x, slot_y, label in self.slots:
            label_text = self.box_font.render(label, True, (0, 0, 0))
            label_rect = label_text.get_rect(center=(slot_x + self.main_board.cell_size // 2, slot_y + self.main_board.cell_size // 2))
            self.screen.blit(label_text, label_rect)

    def handle_shop_interaction(self, current_piece, event):
        # Implement movement logic for the piece in the shop area
        if event.key == K_LEFT:
            if self.main_board.can_move(current_piece, -1, 0):
                current_piece.x -= 1
        elif event.key == K_RIGHT:
            if self.main_board.can_move(current_piece, 1, 0):
                current_piece.x += 1
        elif event.key == K_DOWN:
            if self.main_board.can_move(current_piece, 0, 1):
                current_piece.y += 1
        elif event.key == K_UP:
            # Rotate piece logic in the shop if needed
            pass
        elif event.key == K_SPACE:
            # Hard drop logic in the shop if needed
            pass
        elif event.key == K_c:
            # Hold piece logic in the shop if needed
            pass

