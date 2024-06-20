import pygame
import sys
from pygame.locals import *
from board import Board
from pieces import IPiece, OPiece, TPiece, SPiece, ZPiece, JPiece, LPiece
from random import choice
import random

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 600
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('TetrisRoguelike')

        self.board_width = 10
        self.board_height = 20
        self.cell_size = 20 
        self.board_pixel_width = self.board_width * self.cell_size
        self.board_pixel_height = self.board_height * self.cell_size
        self.offset_x = (self.screen_width - self.board_pixel_width) // 2
        self.offset_y = (self.screen_height - self.board_pixel_height) // 2
        self.delay = 0

        self.board = Board(self.screen)
        self.bag = []
        self.last_piece = None
        self.current_piece = self.new_piece()
        self.held_piece = None
        self.can_hold = True
        self.lines_cleared = 0
        self.running = True

        self.clock = pygame.time.Clock()

        self.ARR = 50  # Auto Repeat Rate 
        self.gravity = 500  # Gravity interval 
        self.DAS = 15  # Delayed Auto Shift 
        self.LockDelay = 500 # How until piece is added to board upon last action
        self.last_move_time = pygame.time.get_ticks()
        self.last_gravity_time = pygame.time.get_ticks()
        self.last_LockDelay = pygame.time.get_ticks()

        self.background_color = (200, 200, 200)  # Light gray background color

        # Initialize key state tracking
        self.key_held = {K_LEFT: False, K_RIGHT: False, K_z: False}
        self.key_initial_time = {K_LEFT: 0, K_RIGHT: 0, K_z: 0}
        self.key_delay_over = {K_LEFT: False, K_RIGHT: False, K_z: False}

        self.game_loop()

    def initialize_bag(self):
        pieces = [IPiece, OPiece, TPiece, SPiece, ZPiece, JPiece, LPiece]
        random.shuffle(pieces)
        self.bag = pieces

    def new_piece(self):
        if not self.bag:
            self.initialize_bag()

        new_piece = self.bag.pop()

        # Avoid immediate repeats
        if new_piece == self.last_piece and self.bag:
            self.bag.insert(0, new_piece)
            new_piece = self.bag.pop()

        self.last_piece = new_piece
        return new_piece()
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # Continuous movement handling
        if keys[K_LEFT]:
            if not self.key_held[K_LEFT]:
                self.key_held[K_LEFT] = True
                self.key_initial_time[K_LEFT] = current_time
                self.handle_movement(self.move_left, initial=True)
            else:
                if not self.key_delay_over[K_LEFT]:
                    if current_time - self.key_initial_time[K_LEFT] >= self.DAS:
                        self.key_delay_over[K_LEFT] = True
                        self.last_move_time = current_time
                if self.key_delay_over[K_LEFT]:
                    self.handle_movement(self.move_left)
        else:
            self.key_held[K_LEFT] = False
            self.key_delay_over[K_LEFT] = False

        if keys[K_RIGHT]:
            if not self.key_held[K_RIGHT]:
                self.key_held[K_RIGHT] = True
                self.key_initial_time[K_RIGHT] = current_time
                self.handle_movement(self.move_right, initial=True)
            else:
                if not self.key_delay_over[K_RIGHT]:
                    if current_time - self.key_initial_time[K_RIGHT] >= self.DAS:
                        self.key_delay_over[K_RIGHT] = True
                        self.last_move_time = current_time
                if self.key_delay_over[K_RIGHT]:
                    self.handle_movement(self.move_right)
        else:
            self.key_held[K_RIGHT] = False
            self.key_delay_over[K_RIGHT] = False

        if keys[K_z]:
            if not self.key_held[K_z]:
                self.key_held[K_z] = True
                self.key_initial_time[K_z] = current_time
                self.handle_movement(self.move_down, initial=True)
            else:
                if not self.key_delay_over[K_z]:
                    if current_time - self.key_initial_time[K_z] >= self.DAS:
                        self.key_delay_over[K_z] = True
                        self.last_move_time = current_time
                if self.key_delay_over[K_z]:
                    self.handle_movement(self.move_down)
        else:
            self.key_held[K_z] = False
            self.key_delay_over[K_z] = False
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

    def handle_movement(self, movement_func, initial=False):
        current_time = pygame.time.get_ticks()
        if initial or current_time - self.last_move_time >= self.ARR:
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
        if current_time - self.last_gravity_time >= self.gravity:
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
                    pygame.draw.rect(self.screen, (128,128,128),
                                     (self.offset_x + x * self.cell_size,
                                      self.offset_y + y * self.cell_size,
                                      self.cell_size, self.cell_size))
        self.draw_ghost_piece()
        
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.current_piece.color,
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
                        pygame.draw.rect(self.screen, self.held_piece.color,
                                         (10 + x * self.cell_size,
                                          10 + y * self.cell_size,
                                          self.cell_size, self.cell_size))

    def game_loop(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(240)  # Cap the frame rate at 240 FPS

if __name__ == "__main__":
    game = Game()
    game.game_loop()
