#high score: 247
import pygame
from copy import copy
import random
import time

pygame.init()
pygame.display.init()
pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
screen = pygame.display.get_surface()

RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(50, 150, 0)
BLUE = pygame.Color(40, 80, 255)
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
GREY1 = pygame.Color(50, 50, 50)

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
temp_color_dict = {0:GREY1, 1:RED, 2:GREEN, 3:BLUE, 4:WHITE, 5:pygame.Color(255, 50, 200),
6:pygame.Color(255, 255, 0), 7:pygame.Color(0, 255, 255), 8:pygame.Color(255, 128, 0), 
9:pygame.Color(170, 30, 255), 10:pygame.Color(150, 150, 150), 11:pygame.Color(40, 255, 100),
12:pygame.Color(0, 0, 0), 13:pygame.Color(80, 80, 80)}

debug_msgs = []
global_frame_count = 0

def debug(msg):
    debug_msgs.append((global_frame_count, str(msg)))

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0 for y in range(self.height)] for x in range(self.width)]

    def in_board(self, x, y):
        if(x < 0 or x >= self.width or y >= self.height):
            return False
        return True

    def get_block(self, x, y):
        if(y < 0):
            return 0
        return self.board[x][y]

    def set_block(self, x, y, block):
        if not self.in_board(x, y):
            return False
        if(y >= 0):
            self.board[x][y] = block
        return True

    def clear_line(self, line):
        for i in range(line, 0, -1):
            for x in range(self.width):
                self.set_block(x, i, self.get_block(x, i - 1))
        for x in range(self.width):
            self.set_block(x, 0, 0)

    def can_place_penta(self, penta):
        for block in penta.blocks:
            if not self.in_board(block[0] + penta.x, block[1] + penta.y):
                return False
            if not self.get_block(block[0] + penta.x, block[1] + penta.y) ==  0:
                return False
        return True

    def set_penta(self, x, y, penta, value = None):
        if(value == None):
            value = penta.blockid + 1
        for block in penta.blocks:
            if not self.in_board(block[0] + x, block[1] + y):
                return False
        for block in penta.blocks:
            self.set_block(block[0] + x, block[1] + y, value)
        return True

    def set_board(self, board):
        for x in range(self.width):
            for y in range(self.height):
                self.set_block(x, y, board.get_block(x, y))

    def draw_block(self, x_block, y_block, x_offset, y_offset):
        color = temp_color_dict[self.board[x_block][y_block]]
        xsize = 20
        ysize = 20
        x_pos = x_offset + xsize*x_block
        y_pos = y_offset + ysize*y_block
        if(self.board[x_block][y_block] == 0 or self.board[x_block][y_block] == 13):
            pygame.draw.rect(screen, color, pygame.Rect(x_pos,     y_pos,     xsize - 1, ysize - 1))
        else:
            dark_color = color//pygame.Color(2, 2 ,2) + pygame.Color(40, 40, 40)
            pygame.draw.rect(screen, dark_color, pygame.Rect(x_pos,     y_pos + 2, xsize - 1, ysize - 3))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x_pos,     y_pos,     xsize - 2, ysize - 2))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x_pos,     y_pos,     xsize - 1, 2))
            pygame.draw.rect(screen, color, pygame.Rect(x_pos + 2, y_pos + 2, xsize - 4, ysize - 4))
            

    def draw(self, x_offset, y_offset, width, height):
        for x in range(len(self.board)):
            for y in range(len(self.board[x])):
                self.draw_block(x, y, x_offset, y_offset)

class Game:
    randomblocks = True
    MOVEMENT_REPEAT = 1
    MOVEMENT_START = 6
    FRAMES_TO_PLACE = 60
    MIN_TIME_BEFORE_LOCK = 20

    def __init__(self):
        self.last_2_pentas = [-1, -1]
        self.game_board = Board(10, 22)
        self.draw_board = Board(10, 22)
        self.current_penta = None
        self.next_penta = None
        self.current_penta = Penta(self.get_random_penta())
        self.next_penta = Penta(self.get_random_penta())
        #self.draw_board.set_penta(self.current_penta.x, self.current_penta.y, self.current_penta)
        self._update_draw_board()
        self.frames_per_drop = 20
        self.frames = self.frames_per_drop
        self.frames_since_input = 0
        self.score = 0
        self.lost = False
        self.fastdrop = False
        self.updated = True
        self.held_penta = None
        self.can_hold = True
        self.trying_to_place = False
        self.frames_since_landed = 0
        self.left_pressed = False
        self.right_pressed = False
        self.ticks_before_left = -1
        self.ticks_before_right = -1

    def get_random_penta(self):
        if(Game.randomblocks):
            blockid = random.randrange(12)
            while(blockid == self.last_2_pentas[0] or blockid == self.last_2_pentas[1]):
                blockid = random.randrange(12)
            self.last_2_pentas[0] = self.last_2_pentas[1]
            self.last_2_pentas[1] = blockid
            return blockid
        else:
            return Penta.nextblock

    def tick(self):
        if(self.lost):
            return
        self.frames_since_input += 1

        if(self.left_pressed):
            self.ticks_before_left -= 1
            if(self.ticks_before_left < 0):
                self.ticks_before_left += Game.MOVEMENT_REPEAT
                self.move_by(-1, 0)
        if(self.right_pressed):
            self.ticks_before_right -= 1
            if(self.ticks_before_right < 0):
                self.ticks_before_right += Game.MOVEMENT_REPEAT
                self.move_by(1, 0)

        if(self.trying_to_place):
            self.frames_since_landed += 1
            is_min_time = self.frames_since_landed > Game.MIN_TIME_BEFORE_LOCK - self.frames_per_drop 
            is_max_time = self.frames_since_landed > self.FRAMES_TO_PLACE
            if(self.move_by(0, 1)):
                self.move_by(0, -1)
                self.trying_to_place = False
            elif(is_min_time and self.frames_since_input > Game.MIN_TIME_BEFORE_LOCK or is_max_time):
                if(not self.move_by(0, 1)):
                    self._place()
                self.trying_to_place = False
                self.frames = self.frames_per_drop
        else:
            if self.fastdrop:
                self.frames -= 5#maybe scale this with fall speed
            else:
                self.frames -= 1

            while(self.frames <= 0):
                if(not self.move_by(0, 1)):
                    self.trying_to_place = True
                    self.frames_since_landed = 0
                self.frames += self.frames_per_drop
            

    def _place(self):
        self.game_board.set_penta(self.current_penta.x, self.current_penta.y, self.current_penta)

        linestoclear = []
        for y in range(self.game_board.height):
            for x in range(self.game_board.width):
                if(self.game_board.get_block(x, y) == 0):
                    break
            else:
                linestoclear.append(y)
        for line in linestoclear:
            self.game_board.clear_line(line)
            self.score += 1

        #check if lose
        self.lost = not self.game_board.can_place_penta(self.next_penta)

        self.can_hold = True

        self.frames = self.frames_per_drop
        new_penta = Penta(self.get_random_penta())
        self.current_penta = self.next_penta
        self.next_penta = new_penta
        self._update_draw_board()

    def _update_draw_board(self):        
        self.draw_board.set_board(self.game_board)
        ghost_penta = copy(self.current_penta)
        while(self.game_board.can_place_penta(ghost_penta)):
            ghost_penta.translate(0, 1)
        ghost_penta.translate(0, -1)
        self.draw_board.set_penta(ghost_penta.x, ghost_penta.y, ghost_penta, 13)
        self.draw_board.set_penta(self.current_penta.x, self.current_penta.y, self.current_penta)
        self.updated = True

    def _try_place(self, new_penta):
        success = self.game_board.can_place_penta(new_penta)
        if(success):
            self.current_penta = new_penta
            self._update_draw_board()
            return True
        else:
            return False

    def drop(self): 
        if(self.lost):
            return
        success = self.move_by(0, 1)
        while success: 
            success = self.move_by(0, 1)
        self._place()

    def hold(self):
        if(self.can_hold):
            if(self.held_penta == None):
                self.held_penta = self.current_penta
                self.current_penta = self.next_penta
                new_penta = Penta(self.get_random_penta())
                self.next_penta = new_penta
            else:
                temp = self.held_penta
                self.held_penta = self.current_penta
                self.current_penta = temp
                self.current_penta.reset_position()
            self.frames = self.frames_per_drop
            self._update_draw_board()
            self.can_hold = False

    def set_left(self, pressed):
        self.left_pressed = pressed
        if(pressed):
            self.ticks_before_left = Game.MOVEMENT_START
            self.right_pressed = False
            self.move_by(-1, 0)

    def set_right(self, pressed):
        self.right_pressed = pressed
        if(pressed):
            self.ticks_before_right = Game.MOVEMENT_START
            self.left_pressed = False
            self.move_by(1, 0)

    def move_by(self, x, y):
        if(self.lost):
            return False
        new_penta = copy(self.current_penta)
        new_penta.translate(x, y)
        success = self._try_place(new_penta)
        if(y == 0 and success):
            self.frames_since_input = 0
        return success

    def find_spot(self, penta):
        success = self._try_place(penta)
        if(not success):
            old_x = penta.x
            old_y = penta.y
            x_try_order = (1, -1, 2, -2)
            y_try_order = (0, -1, -2, 1, 2)#this might be a bit generous
            for y in y_try_order:
                for x in x_try_order:
                    penta.x = old_x + x
                    penta.y = old_y + y
                    success = self._try_place(penta)
                    if(success):
                        break
                if(success):
                    break
        return success

    def rotate(self, direction):
        if(self.lost):
            return False
        new_penta = copy(self.current_penta)
        new_penta.rotate(direction)
        success = self.find_spot(new_penta)
        if(success):
            self.frames_since_input = 0
        return success
        
    def reflect(self):
        if(self.lost):
            return False
        new_penta = copy(self.current_penta)
        new_penta.reflect()
        success = self.find_spot(new_penta)
        if(success):
            self.frames_since_input = 0
        return success

class Penta:
    #order (also names): I, L, k, /, b, c, v, T, w, 7, z, x
    blocktypes = (((2, 0), (1, 0), (0, 0), (-1, 0), (-2, 0)), ((-2, 1), (-1, 1), (0, 1), (1, 1), (-2, 0)),
    ((-2, 1), (-1, 1), (0, 1), (1, 1), (-1, 0)), ((-1, 1), (0, 1), (1, 1), (-2, 0), (-1, 0)),

    ((-1, 1), (0, 1), (1, 1), (-1, 0), (0, 0)), ((-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0)),
    ((1, 2), (1, 1), (1, 0), (0, 2), (-1, 2)), ((-1, 0), (-1, 1), (-1, 2), (0, 1), (1, 1)),

    ((0, 2), (1, 2), (-1, 1), (0, 1), (-1, 0)), ((0, 0), (-1, 0), (1, 1), (0, 1), (0, 2)),
    ((-1, 1), (-1, 2), (0, 1), (1, 0), (1, 1)), ((-1, 1), (0, 0), (0, 1), (0, 2), (1, 1)))

    blockcenters = ((0, 0), (-.5, .5), (-.5, 0.5), (-.5, .5),
    (0, 1), (0, 1), (0, 1), (0, 1),
    (0, 1), (0, 1), (0, 1), (0, 1))

    nextblock = 0

    def __init__(self, blockid):
        self.blockid = blockid
        self.blocks = self.blocktypes[self.blockid]
        Penta.nextblock = (Penta.nextblock + 1)%12
        self.reset_position()

    def reset_position(self):
        self.x = 5
        self.y = 0

    def translate(self, x, y):
        self.x += x
        self.y += y

    def rotate(self, angle):
        newblocks = list(self.blocks)
        for _ in range(angle):
            for i, block in enumerate(newblocks):
                newx = block[0] - self.blockcenters[self.blockid][0]
                newy = block[1] - self.blockcenters[self.blockid][1]
                newx, newy = newy, -newx
                newx = newx + self.blockcenters[self.blockid][0]
                newy = newy + self.blockcenters[self.blockid][1]
                newblocks[i] = (int(newx), int(newy))
        self.blocks = tuple(newblocks)

    def reflect(self):
        newblocks = list(self.blocks)
        for i, block in enumerate(self.blocks):
            newx = 2*self.blockcenters[self.blockid][0] - block[0]
            #newy = 2*self.blockcenters[self.blockid][1] - block[1]
            newy = block[1]
            newblocks[i] = (int(newx), int(newy))
        self.blocks = tuple(newblocks)

game = Game()
quittage = False
font = pygame.font.Font(None, 30)
tinyfont = pygame.font.Font(None, 15)
paused = False
show_controls = False
controls_shown = False
screen_updated = False

last_time = time.monotonic()
fps = 60
show_fps = False

while not quittage:

    if(not game.lost and not pygame.key.get_pressed()[pygame.K_f] and not paused):
        game.tick()

    pygame.display.flip()

    events = pygame.event.get()
    for event in events:
        if(event.type == pygame.QUIT):
            quittage = True
        if(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            show_controls = not show_controls
            screen_updated = True
        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_p):
                if(pygame.key.get_pressed()[pygame.K_q]):
                    paused = not paused
                    print("pause", game.current_penta.blocks, game.current_penta.y)
            if(paused):
                if(event.key == pygame.K_LEFT):
                    game.move_by(-1, 0)
                elif(event.key == pygame.K_RIGHT):
                    game.move_by(1, 0)
                elif(event.key == pygame.K_DOWN):
                    game.move_by(0, 1)
                elif(event.key == pygame.K_UP):
                    game.move_by(0, -1)
                elif(event.key == pygame.K_z):
                    game.rotate(3)
                elif(event.key == pygame.K_o):
                    Game.randomblocks = not Game.randomblocks
                print(game.current_penta.blocks, game.current_penta.y, game.current_penta.blockid)
                continue

            if(event.key == pygame.K_LEFT):
                game.set_left(True)
            elif(event.key == pygame.K_RIGHT):
                game.set_right(True)
            elif(event.key == pygame.K_DOWN):
                game.fastdrop = True
                game.move_by(0, 1)
                game.frames = game.frames_per_drop
            elif(event.key == pygame.K_UP):
                game.rotate(3)
            elif(event.key == pygame.K_z):
                game.rotate(1)
            elif(event.key == pygame.K_x):
                game.reflect()
            elif(event.key == pygame.K_SPACE):
                game.drop()
            elif(event.key == pygame.K_LSHIFT):
                game.hold()
            elif(event.key == pygame.K_r):
                game = Game()
        elif(event.type == pygame.KEYUP):
            if(event.key == pygame.K_DOWN):
                game.fastdrop = False
            if(event.key == pygame.K_LEFT):
                game.set_left(False)
            elif(event.key == pygame.K_RIGHT):
                game.set_right(False)

    global_frame_count += 1
    if(len(debug_msgs) > 0):
        screen_updated = True

    if(game.updated or screen_updated):
        screen.fill(pygame.Color(0, 0, 0))
        if(show_fps):
            screen.blit(font.render("FPS: " + str(int(fps*100)/100), True, WHITE), (0, 300))

        game.draw_board.draw(150, 0, 20, 20)
        screen.blit(font.render("SCORE: " + str(game.score), True, WHITE), (390, 150))
        if(game.lost):
            screen.blit(font.render("GAME OVER", True, WHITE), (400, 40))
        else:
            screen.blit(font.render("HELD PIECE", True, pygame.Color(255, 255, 255)), (0, 0))
            screen.blit(font.render("NEXT PIECE", True, pygame.Color(255, 255, 255)), (390, 0))
            tempboard = Board(5, 5)
            tempboard.set_penta(2, 2, game.next_penta)
            tempboard.draw(390, 25, 17, 17)
            tempboard = Board(5, 5)
            if(game.held_penta != None):
                if(game.can_hold):
                    tempboard.set_penta(2, 2, game.held_penta)
                else:
                    tempboard.set_penta(2, 2, game.held_penta, 13)
            tempboard.draw(0, 25, 17, 17)

        if(show_controls):
            controlstext = ["CONTROLS:", "Left Arrow: Move left", "Right Arrow: Move right", "Down Arrow: Move down", 
                            "Up Arrow: Rotate right", "Z: Rotate left", "X: Flip piece", "Space: Drop piece", 
                            "Left Shift: Hold piece", "R: Restart game"]
            for (i, msg) in enumerate(controlstext):
                screen.blit(font.render(msg, True, pygame.Color(150, 150, 150)), (350, 200 + 20*i))
            controls_shown = True
        elif(not controls_shown):
            screen.blit(font.render("Click to show controls", True, pygame.Color(100, 100, 100)), (400, 400))
            
        msgs = debug_msgs[::-1]
        for (i, msg) in enumerate(msgs):
            brightness = min(max(255 - (global_frame_count - msg[0]), 0), 255)
            screen.blit(tinyfont.render(msg[1], True, pygame.Color(brightness, brightness, brightness)), (200, 10*i))
            if(global_frame_count - msg[0] >= 254):
                del debug_msgs[len(debug_msgs) - i - 1]

        game.updated = False
        screen_updated = False

    now = time.monotonic()
    fps = 1/(now - last_time)
    last_time = now
                
    clock.tick(30)
