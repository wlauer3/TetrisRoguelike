import pygame
import sys
from pygame.locals import *
from board import Board
from pieces import IPiece, OPiece, TPiece, SPiece, ZPiece, JPiece, LPiece
from random import choice
from config import Config
import wallkicks
import random

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = Config.SCREEN_WIDTH
        self.screen_height = Config.SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('TetrisRoguelike')

        self.board_width = Config.BOARD_WIDTH
        self.board_height = Config.BOARD_HEIGHT
        self.cell_size = Config.CELL_SIZE
        self.board_pixel_width = self.board_width * self.cell_size
        self.board_pixel_height = (self.board_height - 2) * self.cell_size  # Adjust for hidden rows
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
        self.LockDelay = 500 # Time piece is added to board upon last action
        self.last_move_time = pygame.time.get_ticks()
        self.last_gravity_time = pygame.time.get_ticks()
        self.lock_delay_start = None  # Timer for lock delay
        self.lock_delay_reset = False  # Flag to reset the lock delay on movement


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
        piece_instance = new_piece()
        piece_instance.y = -2  # Start the piece in the hidden rows
        return piece_instance
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

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

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    self.rotate_clockwise()
                elif event.key == K_DOWN:
                    self.rotate_counterclockwise()
                elif event.key == K_SPACE:
                    self.hard_drop()
                elif event.key == K_c:
                    self.hold_piece()

    def handle_movement(self, movement_func, initial=False):
        current_time = pygame.time.get_ticks()
        if initial or current_time - self.last_move_time >= self.ARR:
            movement_func()
            self.last_move_time = current_time
            self.lock_delay_start = None  # Reset lock delay timer on movement/rotation
            self.lock_delay_reset = True  # Indicate that lock delay should be reset

    def move_left(self):
        if self.board.can_move(self.current_piece, -1, 0):
            self.current_piece.x -= 1

    def move_right(self):
        if self.board.can_move(self.current_piece, 1, 0):
            self.current_piece.x += 1

    def move_down(self):
        if self.board.can_move(self.current_piece, 0, 1):
            self.current_piece.y += 1

    def rotate_piece(self, reverse=False):
        initial_state = self.current_piece.current_state
        self.current_piece.rotate(reverse)
        final_state = self.current_piece.current_state

        kicks = wallkicks.get_wall_kicks(self.current_piece.type, initial_state, final_state)

        for x_offset, y_offset in kicks:
            if self.board.can_move(self.current_piece, x_offset, y_offset):
                self.current_piece.x += x_offset
                self.current_piece.y += y_offset
                return
        # If no valid kicks, revert to original state
        self.current_piece.rotate(not reverse)

    def rotate_clockwise(self):
        self.rotate_piece(reverse=False)

    def rotate_counterclockwise(self):
        self.rotate_piece(reverse=True)

    def hard_drop(self):
        while self.board.can_move(self.current_piece, 0, 1):
            self.current_piece.y += 1
        self.lock_piece()  # Lock the piece immediately on hard drop
        
        # Check if the piece is in row 23 or higher
        if self.current_piece.y >= 22:
            self.running = False
            print(f"Game Over! Your score: {self.lines_cleared} lines cleared")
            return

        lines_cleared = self.board.clear_lines()
        self.lines_cleared += lines_cleared
        self.current_piece = self.new_piece()
        self.can_hold = True

        if not self.board.can_move(self.current_piece, 0, 0):
            self.running = False
            print(f"Game Over! Your score: {self.lines_cleared} lines cleared")



    def hold_piece(self):
        if not self.can_hold:
            return
        if self.held_piece is None:
            self.held_piece = self.current_piece
            self.current_piece = self.new_piece()
        else:
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
        self.current_piece.x = self.board_width // 2 - len(self.current_piece.shape[0]) // 2
        self.current_piece.y = -2  # Start the piece in the hidden rows
        self.can_hold = False
        self.lock_delay_start = None  # Reset lock delay timer on hold
        self.lock_delay_reset = True  # Indicate that lock delay should be reset

    def lock_piece(self):
        self.board.add_piece(self.current_piece)
        lines_cleared = self.board.clear_lines()
        self.lines_cleared += lines_cleared
        self.current_piece = self.new_piece()
        self.can_hold = True
        self.lock_delay_start = None  # Reset the lock delay timer for the new piece
        self.lock_delay_reset = False  # Reset the lock delay reset flag

        if not self.board.can_move(self.current_piece, 0, 0):
            self.running = False
            print(f"Game Over! Your score: {self.lines_cleared} lines cleared")

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_gravity_time >= self.gravity:
            if self.board.can_move(self.current_piece, 0, 1):
                self.current_piece.y += 1
                self.lock_delay_start = None  # Reset lock delay timer on movement
                self.lock_delay_reset = False  # Piece moved down, reset should not apply
            else:
                if self.lock_delay_start is None:
                    self.lock_delay_start = current_time
                elif current_time - self.lock_delay_start >= self.LockDelay:
                    if not self.lock_delay_reset:
                        self.lock_piece()
                    else:
                        self.lock_delay_start = current_time  # Reset the timer if there was a recent move

            self.last_gravity_time = current_time




    def draw(self):
        self.screen.fill(self.background_color)

        for y in range(2, self.board.height):  # Skip the top 2 rows
            for x, cell in enumerate(self.board.grid[y]):
                if cell:
                    pygame.draw.rect(self.screen, (128, 128, 128),
                                    (self.offset_x + x * self.cell_size,
                                    self.offset_y + (y - 2) * self.cell_size,  # Adjust for hidden rows
                                    self.cell_size, self.cell_size))
        self.draw_ghost_piece()

        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    draw_y = self.current_piece.y + y - 2
                    pygame.draw.rect(self.screen, self.current_piece.color,
                                    (self.offset_x + (self.current_piece.x + x) * self.cell_size,
                                    self.offset_y + draw_y * self.cell_size,
                                    self.cell_size, self.cell_size))

        # Draw the three-sided border, leaving the top open
        pygame.draw.line(self.screen, (0, 0, 0), 
                        (self.offset_x, self.offset_y + self.board_pixel_height), 
                        (self.offset_x + self.board_pixel_width, self.offset_y + self.board_pixel_height), 4)
        pygame.draw.line(self.screen, (0, 0, 0), 
                        (self.offset_x, self.offset_y), 
                        (self.offset_x, self.offset_y + self.board_pixel_height), 4)
        pygame.draw.line(self.screen, (0, 0, 0), 
                        (self.offset_x + self.board_pixel_width, self.offset_y), 
                        (self.offset_x + self.board_pixel_width, self.offset_y + self.board_pixel_height), 4)

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
                    draw_y = ghost_piece.y + y - 2  # Adjust for hidden rows
                    if draw_y >= 0:
                        pygame.draw.rect(self.screen, (169, 169, 169),
                                        (self.offset_x + (ghost_piece.x + x) * self.cell_size,
                                        self.offset_y + draw_y * self.cell_size,
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
