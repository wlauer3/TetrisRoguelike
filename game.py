import pygame
import sys
from pygame.locals import *
from board import Board
from pieces import IPiece, OPiece, TPiece, SPiece, ZPiece, JPiece, LPiece
from random import choice
from config import Config
import wallkicks
import random
from score_manager import ScoreManager
from level_manager import LevelManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = Config.SCREEN_WIDTH
        self.screen_height = Config.SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('TetrisRoguelike')

        self.board_width = Config.BOARD_WIDTH
        self.board_height = 22
        self.cell_size = Config.CELL_SIZE
        self.board_pixel_width = self.board_width * self.cell_size
        self.board_pixel_height = (self.board_height - 2) * self.cell_size  # Adjust for hidden rows
        self.offset_x = (self.screen_width - self.board_pixel_width) // 2
        self.offset_y = (self.screen_height - self.board_pixel_height) // 2
        self.delay = 0
        self.score = 0  # Initialize the score attribute
        self.shop_slots = [1, 2, 3, 4, 5, 6, 7, 8]  # Define slots
        self.shop_slot_grids = []
        self.shop_items = [0,0,0]
        self.shop_phase = False
        self.initialize_shop_slots()
        self.shop_x_cells = [0, 0, 0]
        self.shop_y_cells = [0, 0, 0]
        self.shop_initialized = False
        self.shop_initial_x = [0 ,0 ,0]
        
        
        self.level_manager = LevelManager()
        self.score_manager = ScoreManager(self.level_manager)
        self.board = Board(self.screen, self.shop_phase)
        self.bag = []
        self.last_piece = None
        self.current_piece = self.new_piece()
        self.held_piece = None
        self.can_hold = True
        self.lines_cleared = 0
        self.running = True

        self.clock = pygame.time.Clock()

        self.ARR = 32  # Auto Repeat Rate 
        self.gravity = 500  # Gravity interval 
        self.storeGrav = self.gravity
        self.DAS = 68  # Delayed Auto Shift 
        self.LockDelay = 500 # Time piece is added to board upon last action
        self.last_move_time = pygame.time.get_ticks()
        self.last_gravity_time = pygame.time.get_ticks()
        self.lock_delay_start = None  # Timer for lock delay
        self.lock_delay_reset = False  # Flag to reset the lock delay on movements

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
                    self.rotate_piece(reverse=False)
                elif event.key == K_DOWN:
                    self.rotate_piece(reverse=True)
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
        if self.board.can_move(self.current_piece, -1, 0, self.shop_phase):
            self.current_piece.x -= 1

    def move_right(self):
        if self.board.can_move(self.current_piece, 1, 0, self.shop_phase):
            self.current_piece.x += 1

    def move_down(self):
        if self.board.can_move(self.current_piece, 0, 1, self.shop_phase):
            self.current_piece.y += 1

    def rotate_piece(self, reverse=False):
        self.lock_delay_start = None
        initial_state = self.current_piece.current_state
        if reverse:
            self.current_piece.current_state = (self.current_piece.current_state - 1) % len(self.current_piece.states)
        else:
            self.current_piece.current_state = (self.current_piece.current_state + 1) % len(self.current_piece.states)
        final_state = self.current_piece.current_state
        self.current_piece.shape = self.current_piece.states[self.current_piece.current_state]

        kicks = wallkicks.get_wall_kicks(self.current_piece.type, initial_state, final_state)

        for x_offset, y_offset in kicks:
            if self.board.can_move(self.current_piece, x_offset, y_offset, self.shop_phase):
                self.current_piece.x += x_offset
                self.current_piece.y += y_offset
                print(f"Rotation successful with wall kick offset: ({x_offset}, {y_offset})")
                return

        # If no valid kicks, revert to original state
        self.current_piece.current_state = initial_state
        self.current_piece.shape = self.current_piece.states[self.current_piece.current_state]
        print("Rotation reverted to original state")

    def hard_drop(self):
        while self.board.can_move(self.current_piece, 0, 1, self.shop_phase):
            self.current_piece.y += 1
        self.lock_piece()  # Lock the piece immediately on hard drop

        lines_cleared = self.board.clear_lines(self.score_manager)
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
            self.current_piece.y = 0  # Start the piece in the hidden rows
            self.current_piece.current_state = 0  # Reset to original state
            self.current_piece.shape = self.current_piece.states[0]  # Update the shape
        self.can_hold = False
        self.lock_delay_start = None  # Reset lock delay timer on hold
        self.lock_delay_reset = True  # Indicate that lock delay should be reset

    def lock_piece(self):
        self.board.add_piece(self.current_piece)
        self.board.clear_lines(self.score_manager)

        self.score = self.score_manager.get_score()
        self.lines_cleared = self.score_manager.get_lines_cleared()
        self.gravity = self.score_manager.get_gravity()
        
        self.current_piece = self.new_piece()
        self.can_hold = True
        self.lock_delay_start = None  # Reset the lock delay timer for the new piece
        self.lock_delay_reset = False  # Reset the lock delay reset flag

        if any(self.board.grid[y][x] != 0 for y in range(1) for x in range(self.board.width)):
            self.running = False
            print(f"Game Over! Your score: {self.lines_cleared} lines cleared, Total Score: {self.score_manager.get_score()}")

    def initialize_shop_slots(self):
        if not self.shop_phase:
            print(f"Initializing the shop")
            random.shuffle(self.shop_slots)
            self.shop_slot_y_positions = []  # List to store the Y positions of the slots
            self.shop_slot_y_cells = []
            self.shop_x = []
            self.shop_items = []
            self.shop_y = []
            for _ in range(3):  # Number of shop items available
                y_position = self.offset_y + random.randint(4, 17) * self.cell_size  # Random Y position for each slot
                y_cell = int((y_position - self.offset_y)/self.cell_size) + 2
                self.shop_slot_y_positions.append(y_position)
                self.shop_slot_y_cells.append(y_cell)
                self.shop_y.append(y_cell)
                self.shop_items.append(y_cell)
            self.shop_y_cells = self.shop_y
        self.shop_phase = True

    def draw_shop(self):
        xpos = self.board.width * self.cell_size + self.offset_x + 2 * self.cell_size  # Adjust xpos to be next to the main board
        if(self.shop_items[0] == 0):
            slot2 = 0
        if(self.shop_items[1] == 0):
            slot3 = 0
        
        # Draw the slots
        for i in range(3):  # Number of shop items available
            slot_width = 0
            slot_type = self.shop_slots[i]
            if slot_type == 1:
                slot_width = 1  # Width for IPiece Slot
            elif slot_type == 2:
                slot_width = 2  # Width for OPiece Slot
            elif slot_type == 3:
                slot_width = 3  # Width for TPiece Slot
            elif slot_type == 4:
                slot_width = 2  # Width for JorLPiece Slot
            elif slot_type == 5:
                slot_width = 2  # Width for ZPiece slot
            elif slot_type == 6:
                slot_width = 2  # Width for SPiece slot
            elif slot_type == 7:
                slot_width = 2  # Width for LPiece slot
            elif slot_type == 8:
                slot_width = 2  # Width for JPiece slot
            if(self.shop_items[i] != 0):
                if (i == 0):
                    slot = self.board.width + 1
                    slot2 = slot_width
                    self.shop_x.append(slot)  
                if (i == 1):
                    if(self.shop_initialized == False):
                        slot = self.board.width + slot2 + 3
                        slot3 = slot_width
                        self.shop_x.append(slot)
                    if(self.shop_initialized == True):
                        if(slot2 == 0):
                            slot = self.board.width + self.shop_initial_x[1] + 3
                        if(slot2 != 0):
                            slot = self.board.width + slot2 + 3
                        slot3 = slot_width
                        self.shop_x.append(slot)
                if (i == 2):
                    if(self.shop_initialized == False):
                        slot = self.board.width + slot2 + slot3 + 5
                        self.shop_x.append(slot)
                    if(self.shop_initialized == True):
                        if(slot2 == 0 and slot3 == 0):  
                            slot = self.board.width + self.shop_initial_x[1] + self.shop_initial_x[2] + 5
                        elif(slot2 == 0 and slot3 != 0):
                            slot = self.board.width + self.shop_initial_x[1] + slot3 + 5
                        elif(slot2 != 0 and slot3 == 0):
                            slot = self.board.width + slot2 + self.shop_initial_x[2] + 5
                        elif(slot2 != 0 and slot3 != 0):
                            slot = self.board.width + slot2 + slot3 + 5
                        self.shop_x.append(slot)
                ypos = self.shop_slot_y_positions[i]  # Use the stored Y position
                self.draw_shop_slot(i, xpos, ypos, slot)
            xpos += (slot_width * self.cell_size) + (2 * self.cell_size)  # Adjust spacing for next slot
        
        if (self.shop_initialized == False):
            self.shop_initial_x[0] = slot
            self.shop_initial_x[1] = slot2
            self.shop_initial_x[2] = slot3
            self.shop_initialized = True

    def draw_shop_slot(self, index, xpos, ypos, slot):
        slot_type = self.shop_slots[index]
        if(self.shop_items[index] != 0):
            if slot_type == 1:
                self.draw_i_piece_slot(xpos, ypos, slot, index)
            elif slot_type == 2:
                self.draw_o_piece_slot(xpos, ypos, slot, index)
            elif slot_type == 3:
                self.draw_t_piece_slot(xpos, ypos, slot, index)
            elif slot_type == 4:
                self.draw_jorl_piece_slot(xpos, ypos, slot, index)
            elif slot_type == 5:
                self.draw_z_piece_slot(xpos, ypos, slot, index)
            elif slot_type == 6:
                self.draw_s_piece_slot(xpos, ypos, slot, index)
            elif slot_type == 7:
                self.draw_l_piece_slot(xpos, ypos, slot, index)
            elif slot_type == 8:
                self.draw_j_piece_slot(xpos, ypos, slot, index)

            # Check if slot is fully occupied
            if self.is_slot_filled(index, self.shop_slots):
                self.attempt_to_purchase(index, self.shop_slots)
                print(f"Slot filled")

    def is_slot_filled(self, index, shop_slots):
        slot_type = shop_slots[index]
        if slot_type == 1:  # I piece
            return(self.board.grid[self.shop_y[index]][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+3][self.shop_x[index]+1] == 2)
        if slot_type == 2:  # O piece
            return(self.board.grid[self.shop_y[index]][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] == 2)
        if slot_type == 3:  # T piece
            return(self.board.grid[self.shop_y[index]][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]][self.shop_x[index]+3] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] == 2)
        if slot_type == 4:  # JorL piece
            return(self.board.grid[self.shop_y[index]][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]+3][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+3][self.shop_x[index]+2] == 2)
        if slot_type == 5:  # Z piece
            return(self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]][self.shop_x[index]+2] == 2)
        if slot_type == 6:  # S piece
            return(self.board.grid[self.shop_y[index]][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] == 2)
        if slot_type == 7:  # L piece
            return(self.board.grid[self.shop_y[index]][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] == 2)
        if slot_type == 8:  # J piece
            return(self.board.grid[self.shop_y[index]][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]][self.shop_x[index]+2] == 2 and
                   self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] == 2 and
                   self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] == 2)
        return False

    def attempt_to_purchase(self, index, shop_slots):
        slot_type = shop_slots[index]
        if slot_type == 1:  # I piece
            self.board.grid[self.shop_y[index]][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]+1] = 0

            self.board.grid[self.shop_y[index]][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+4][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+2] = 0
        if slot_type == 2:  # O piece
            self.board.grid[self.shop_y[index]][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] = 0

            self.board.grid[self.shop_y[index]][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+3] = 0
        if slot_type == 3:  # T piece
            self.board.grid[self.shop_y[index]][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] = 0

            self.board.grid[self.shop_y[index]][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+4] = 0
        if slot_type == 4:  # JorL piece
            self.board.grid[self.shop_y[index]][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]+2] = 0

            self.board.grid[self.shop_y[index]][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+4][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+4][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+3] = 0
        if slot_type == 5:  # S piece
            self.board.grid[self.shop_y[index]][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] = 0

            self.board.grid[self.shop_y[index]+1][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+3] = 0
        if slot_type == 6:  # Z piece
            self.board.grid[self.shop_y[index]][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] = 0

            self.board.grid[self.shop_y[index]][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+3] = 0
        if slot_type == 7:  # L piece
            self.board.grid[self.shop_y[index]][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] = 0

            self.board.grid[self.shop_y[index]][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+3] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+3] = 0
        if slot_type == 8:  # J piece
            self.board.grid[self.shop_y[index]][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+1] = 0

            self.board.grid[self.shop_y[index]][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]] = 0
            self.board.grid[self.shop_y[index]+3][self.shop_x[index]+1] = 0
            self.board.grid[self.shop_y[index]+2][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]+1][self.shop_x[index]+2] = 0
            self.board.grid[self.shop_y[index]][self.shop_x[index]+3] = 0
        self.shop_items[index] = 0 

    def draw_i_piece_slot(self, xpos, ypos, x, y):

        self.board.grid[self.shop_slot_y_cells[y]][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+3][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+4][x+1] = 1
        self.board.grid[self.shop_slot_y_cells[y]+3][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]][x+2] = 1

        pygame.draw.line(self.screen, (0, 0, 0), (xpos, ypos), (xpos, 4 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, 4 * self.cell_size + ypos), (xpos + 1 * self.cell_size, 4 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1 * self.cell_size, 4 * self.cell_size + ypos), (xpos + 1 * self.cell_size, ypos), 4)

    def draw_o_piece_slot(self, xpos, ypos, x, y):

        self.board.grid[self.shop_slot_y_cells[y]][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+1] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+3] = 1
        self.board.grid[self.shop_slot_y_cells[y]][x+3] = 1

        pygame.draw.line(self.screen, (0, 0, 0), (xpos, ypos), (xpos, 2 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, 2 * self.cell_size + ypos), (xpos + 2 * self.cell_size, 2 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 2 * self.cell_size, 2 * self.cell_size + ypos), (xpos + 2 * self.cell_size, ypos), 4)

    def draw_t_piece_slot(self, xpos, ypos, x, y):

        self.board.grid[self.shop_slot_y_cells[y]][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+1] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+3] = 1
        self.board.grid[self.shop_slot_y_cells[y]][x+4] = 1

        pygame.draw.line(self.screen, (0, 0, 0), (xpos, ypos), (xpos, 1 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, 1 * self.cell_size + ypos), (xpos + 1 * self.cell_size, 1 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1 * self.cell_size, 1 * self.cell_size + ypos), (xpos + 1 * self.cell_size, 2 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1 * self.cell_size, 2 * self.cell_size + ypos), (xpos + 2 * self.cell_size, 2 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 2 * self.cell_size, 2 * self.cell_size + ypos), (xpos + 2 * self.cell_size, 1 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 2 * self.cell_size, 1 * self.cell_size + ypos), (xpos + 3 * self.cell_size, 1 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 3 * self.cell_size, 1 * self.cell_size + ypos), (xpos + 3 * self.cell_size, ypos), 4)

    def draw_jorl_piece_slot(self, xpos, ypos, x, y):

        self.board.grid[self.shop_slot_y_cells[y]][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+3][x] = 1
        
        self.board.grid[self.shop_slot_y_cells[y]+4][x+1] = 1
        self.board.grid[self.shop_slot_y_cells[y]+4][x+2] = 1

        self.board.grid[self.shop_slot_y_cells[y]+3][x+3] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+3] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+3] = 1
        self.board.grid[self.shop_slot_y_cells[y]][x+3] = 1
      
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, ypos), (xpos, 4 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, 4 * self.cell_size + ypos), (xpos + 2 * self.cell_size, 4 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 2 * self.cell_size, 4 * self.cell_size + ypos), (xpos + 2 * self.cell_size, ypos), 4)

    def draw_z_piece_slot(self, xpos, ypos, x, y):

        self.board.grid[self.shop_slot_y_cells[y]+1][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+3][x+1] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+3] = 1
        self.board.grid[self.shop_slot_y_cells[y]][x+3] = 1

        pygame.draw.line(self.screen, (0, 0, 0), (xpos, ypos+1*self.cell_size), (xpos, ypos +3*self.cell_size), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, ypos +3*self.cell_size), (xpos + 1 * self.cell_size, ypos+3*self.cell_size), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1 * self.cell_size, ypos+3*self.cell_size), (xpos + 1 * self.cell_size, ypos +2*self.cell_size), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1 * self.cell_size, ypos +2*self.cell_size), (xpos + 2 * self.cell_size, ypos +2*self.cell_size), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 2 * self.cell_size, ypos +2*self.cell_size), (xpos + 2 * self.cell_size, ypos), 4)
    
    def draw_s_piece_slot(self, xpos, ypos, x, y):

        self.board.grid[self.shop_slot_y_cells[y]][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+1] = 1
        self.board.grid[self.shop_slot_y_cells[y]+3][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+3] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+3] = 1

        pygame.draw.line(self.screen, (0, 0, 0), (xpos, ypos), (xpos, 2 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, 2 * self.cell_size + ypos), (xpos + 1 * self.cell_size, 2 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1 * self.cell_size, 2 * self.cell_size + ypos), (xpos + 1 * self.cell_size, 3 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1 * self.cell_size, 3 * self.cell_size + ypos), (xpos + 2 * self.cell_size, 3 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 2 * self.cell_size, 3 * self.cell_size + ypos), (xpos + 2 * self.cell_size, 1 * self.cell_size + ypos), 4)

    def draw_l_piece_slot(self, xpos, ypos, x, y):
        
        self.board.grid[self.shop_slot_y_cells[y]][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+1] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+1] = 1
        self.board.grid[self.shop_slot_y_cells[y]+3][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+3] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+3] = 1
        self.board.grid[self.shop_slot_y_cells[y]][x+3] = 1

        pygame.draw.line(self.screen, (0, 0, 0), (xpos, ypos), (xpos, 1 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, 1 * self.cell_size + ypos), (xpos + 1 * self.cell_size, 1 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1 * self.cell_size, 1 * self.cell_size + ypos), (xpos + 1 * self.cell_size, 3 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1 * self.cell_size, 3 * self.cell_size + ypos), (xpos + 2 * self.cell_size, 3 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 2 * self.cell_size, 3 * self.cell_size + ypos), (xpos + 2 * self.cell_size, ypos), 4)

    def draw_j_piece_slot(self, xpos, ypos, x, y):

        self.board.grid[self.shop_slot_y_cells[y]][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x] = 1
        self.board.grid[self.shop_slot_y_cells[y]+3][x+1] = 1
        self.board.grid[self.shop_slot_y_cells[y]+2][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]+1][x+2] = 1
        self.board.grid[self.shop_slot_y_cells[y]][x+3] = 1
        
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, ypos), (xpos, 3 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos, 3 * self.cell_size + ypos), (xpos + 1*self.cell_size, 3 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1*self.cell_size, 3 * self.cell_size + ypos), (xpos + 1*self.cell_size, 1 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 1*self.cell_size, 1 * self.cell_size + ypos), (xpos + 2*self.cell_size, 1 * self.cell_size + ypos), 4)
        pygame.draw.line(self.screen, (0, 0, 0), (xpos + 2*self.cell_size, 1 * self.cell_size + ypos), (xpos + 2*self.cell_size, ypos), 4)

    def draw_info(self):
        level = self.level_manager.get_level()
        current_lock_time = 0 if self.lock_delay_start is None else max(0, self.LockDelay - (pygame.time.get_ticks() - self.lock_delay_start))
        score_text = f"Score: {self.score_manager.get_score()}\nLines Cleared: {self.score_manager.get_lines_cleared()}\nLevel: {level}\nARR: {self.ARR}\nDAS: {self.DAS}\nGravity: {self.score_manager.get_gravity()}\nLockTime: {current_lock_time}\nCoords:({self.current_piece.x},{self.current_piece.y}\nWidth:{self.board_width}) "
        font = pygame.font.Font(None, 30)
        
        # Split the score_text into separate lines
        lines = score_text.split('\n')
        
        for i, line in enumerate(lines):
                text = font.render(line, True, (0, 0, 0))
                # Adjust the text_rect to position each line correctly
                text_rect = text.get_rect(topleft=(self.cell_size, 2 * self.cell_size + self.offset_y + i * 40))
                self.screen.blit(text, text_rect)

        if level in [1, 6, 11, 16, 21, 26]:
            self.initialize_shop_slots()
            self.draw_shop()
            self.shop_phase = True
            self.storeGrav = self.gravity
            self.gravity = 500
        else:
            self.shop_phase = False
            self.gravity = self.storeGrav
            self.shop_initialized = False
            self.board.clear_shop_area()  # Clear the shop area

        pygame.display.update()
    
    def update(self):
        if(self.shop_phase):
            self.storeGrav = self.gravity
            self.gravity = 500
        current_time = pygame.time.get_ticks()
        if current_time - self.last_gravity_time >= self.gravity:
            if self.board.can_move(self.current_piece, 0, 1, self.shop_phase):
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

        # Additional check for soft drop lock
        if not self.board.can_move(self.current_piece, 0, 1, self.shop_phase):
            if self.lock_delay_start is None:
                self.lock_delay_start = current_time
            elif current_time - self.lock_delay_start >= self.LockDelay:
                if not self.lock_delay_reset:
                    self.lock_piece()
                else:
                    self.lock_delay_start = current_time  # Reset the timer if there was a recent move
                    if (self.board.can_move(self.current_piece, 0, 1, self.shop_phase) == False):
                        self.lock_piece()

            self.last_gravity_time = current_time

    def draw(self):
        self.screen.fill(self.background_color)
        self.draw_ghost_piece()

        # Draw the current piece
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    draw_y = self.current_piece.y + y - 2
                    draw_x = self.current_piece.x + x
                    pygame.draw.rect(self.screen, self.current_piece.color,
                            (self.offset_x + draw_x * self.cell_size,
                            self.offset_y + draw_y * self.cell_size,
                            self.cell_size, self.cell_size))
        
        self.board.draw_borders(self.offset_x, self.offset_y, self.shop_phase)

        # Draw the three-sided border, leaving the top open
        pygame.draw.line(self.screen, (0, 0, 0), 
                        (self.offset_x, self.offset_y + self.board_pixel_height + 2*self.cell_size), 
                        (self.offset_x + self.board_pixel_width, self.offset_y + self.board_pixel_height + 2*self.cell_size), 4)
        pygame.draw.line(self.screen, (0, 0, 0), 
                        (self.offset_x, self.offset_y + 2*self.cell_size), 
                        (self.offset_x, self.offset_y + self.board_pixel_height + 2*self.cell_size), 4)
        pygame.draw.line(self.screen, (0, 0, 0), 
                        (self.offset_x + self.board_pixel_width, self.offset_y + 2*self.cell_size), 
                        (self.offset_x + self.board_pixel_width, self.offset_y + self.board_pixel_height + 2*self.cell_size), 4)
        
        if self.shop_phase:
            self.draw_shop()

        self.draw_held_piece()
        self.draw_info()

        pygame.display.update()

    def draw_ghost_piece(self):
        ghost_piece = self.current_piece.copy()
        while self.board.can_move(ghost_piece, 0, 1, self.shop_phase):
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
 