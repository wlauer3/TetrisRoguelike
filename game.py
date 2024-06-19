import pygame
import sys
from pygame.locals import *
from board import Board
from pieces import IPiece, OPiece, TPiece, SPiece, ZPiece, JPiece, LPiece
from random import choice

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 512
        self.screen_height = 512
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Tetris')

        self.board_width = 10
        self.board_height = 20
        self.cell_size = 20  # Adjust cell size for better visual alignment
        self.board_pixel_width = self.board_width * self.cell_size
        self.board_pixel_height = self.board_height * self.cell_size
        self.offset_x = (self.screen_width - self.board_pixel_width) // 2
        self.offset_y = (self.screen_height - self.board_pixel_height) // 2
        self.delay = 0

        self.board = Board(self.screen)  # Pass pygame screen surface to Board
        self.current_piece = self.new_piece()
        self.held_piece = None
        self.can_hold = True
        self.lines_cleared = 0
        self.running = True

        self.clock = pygame.time.Clock()

        self.ARR = 50  # Movement interval in milliseconds (adjust as needed)
        self.DAS = 30
        self.gravity_interval = 500  # Gravity interval in milliseconds (adjust as needed)
        self.last_move_time = pygame.time.get_ticks()
        self.last_gravity_time = pygame.time.get_ticks()

        self.background_color = (200, 200, 200)  # Light gray background color

        self.game_loop()

    def new_piece(self):
        pieces = [IPiece, OPiece, TPiece, SPiece, ZPiece, JPiece, LPiece]
        return choice(pieces)()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Continuous movement handling
        if keys[K_LEFT]:

            self.handle_movement(self.move_left)
        elif keys[K_RIGHT]:
            self.handle_movement(self.move_right)
        elif keys[K_z]:
            self.handle_movement(self.move_down)
        
        # Single key press handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    self.rotate_clockwise()
                elif event.key == K_SPACE:
                    self.hard_drop()
                elif event.key == K_c:
                    self.hold_piece()


    def handle_movement(self, movement_func):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.ARR:
            movement_func()
            self.last_move_time = current_time

    def move_left(self):
        if self.board.can_move(self.current_piece, -1, 0):
            self.current_piece.x -= 1

    def move_right(self):
        if self.board.can_move(self.current_piece, 1, 0):
            self.current_piece.x += 1

    def move_down(self):
        if self.board.can_move(self.current_piece, 0, 1):
            self.current_piece.y += 1

    def rotate_clockwise(self):
        self.current_piece.rotate()
        if not self.board.can_move(self.current_piece, 0, 0):
            self.current_piece.rotate(reverse=True)

    def hard_drop(self):
        while self.board.can_move(self.current_piece, 0, 1):
            self.current_piece.y += 1
        self.board.add_piece(self.current_piece)
        lines_cleared = self.board.clear_lines()
        self.lines_cleared += lines_cleared
        self.current_piece = self.new_piece()
        self.can_hold = True

    def hold_piece(self):
        if not self.can_hold:
            return
        if self.held_piece is None:
            self.held_piece = self.current_piece
            self.current_piece = self.new_piece()
        else:
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
        self.current_piece.x = self.board_width // 2 - len(self.current_piece.shape[0]) // 2
        self.current_piece.y = 0
        self.can_hold = False

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_gravity_time >= self.gravity_interval:
            if self.board.can_move(self.current_piece, 0, 1):
                self.current_piece.y += 1
            else:
                self.board.add_piece(self.current_piece)
                lines_cleared = self.board.clear_lines()
                self.lines_cleared += lines_cleared
                self.current_piece = self.new_piece()
                self.can_hold = True

                if not self.board.can_move(self.current_piece, 0, 0):
                    self.running = False
                    print(f"Game Over! Your score: {self.lines_cleared} lines cleared")

            self.last_gravity_time = current_time

    def draw(self):
        self.screen.fill(self.background_color)

        for y, row in enumerate(self.board.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, (0, 0, 255),
                                     (self.offset_x + x * self.cell_size,
                                      self.offset_y + y * self.cell_size,
                                      self.cell_size, self.cell_size))
        self.draw_ghost_piece()
        
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, (255, 0, 0),
                                     (self.offset_x + (self.current_piece.x + x) * self.cell_size,
                                      self.offset_y + (self.current_piece.y + y) * self.cell_size,
                                      self.cell_size, self.cell_size))
                    
        pygame.draw.rect(self.screen, (0, 0, 0),
                         (self.offset_x, self.offset_y,
                          self.board_pixel_width, self.board_pixel_height), 5)

        
        self.draw_held_piece()

        score_text = f"Lines Cleared: {self.lines_cleared}"
        font = pygame.font.Font(None, 36)
        text = font.render(score_text, True, (0, 0, 0))  # Render text with black color
        text_rect = text.get_rect(center=(self.screen_width // 2, self.offset_y + self.board_pixel_height + 20))
        self.screen.blit(text, text_rect)

        pygame.display.update()

    def draw_ghost_piece(self):
        ghost_piece = self.current_piece.copy()
        while self.board.can_move(ghost_piece, 0, 1):
            ghost_piece.y += 1

        for y, row in enumerate(ghost_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, (169, 169, 169),
                                     (self.offset_x + (ghost_piece.x + x) * self.cell_size,
                                      self.offset_y + (ghost_piece.y + y) * self.cell_size,
                                      self.cell_size, self.cell_size))

    def draw_held_piece(self):
        if self.held_piece:
            for y, row in enumerate(self.held_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, (0, 255, 0),
                                         (10 + x * self.cell_size,
                                          10 + y * self.cell_size,
                                          self.cell_size, self.cell_size))

    def game_loop(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)  # Cap the frame rate at 60 FPS

if __name__ == "__main__":
    game = Game()
    game.game_loop()
