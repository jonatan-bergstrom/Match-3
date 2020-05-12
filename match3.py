import random
import pygame
from pygame.locals import *
import numpy as np
import sys
import copy

random.seed()

BOARD_SIZE = 8

CELL_SIZE = 50
Y_OFFSET = CELL_SIZE
COLORS = {
    0 : (253,253,253),
    1 : (235, 64, 52),
    2: (255, 251, 0),
    3 : (0, 194, 16),
    4 : (0, 112, 250),
    5 : (212, 0, 250),
    6 : (255, 162, 0)
}
NUM_COLORS = len(COLORS)
WAIT_TIME = 500


class Move:
    def __init__(self, r0, c0, r1, c1, score = 0, rm = None):
        self.r0 = min(r0, r1)
        self.c0 = min(c0, c1)
        self.r1 = max(r0, r1)
        self.c1 = max(c0, c1)
        self.coord = (self.r0, self.c0, self.r1, self.c1)
        self.score = score
        self.rm = rm


    def __str__(self):
        return f"{self.r0} {self.c0} {self.r1} {self.c1}"


class Game:
    def __init__(self):
        # Generate board
        self.new_board()

        self.score = 0
        self.selected = None
        self.valid_moves = None
        self.accepting_input = True
        self.timer = 0
        self.clock = pygame.time.Clock()


    def new_board(self):
        self.board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self.board[r][c] = self.new_gem(r, c)


    def new_gem(self, r, c):
        choices = list(range(NUM_COLORS))
        random.shuffle(choices)

        while True:
            if len(choices) == 0: # This can't happen, right?
                self.__init__()
                break

            choice = choices.pop()
            try:
                if choice == self.board[r - 1][c] and choice == self.board[r - 2][c]:
                    pass
                elif choice == self.board[r][c - 1] and choice == self.board[r][c - 2]:
                    pass
                else:
                    return choice
            except:
                return choice


    def possible_moves(self):
        # returns true if any move is possible
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE - 1):
                m = Move(r, c, r, c + 1)
                temp_board = copy.deepcopy(self.board)
                self.move(m, temp_board)
                score, rem = self.check_matches(temp_board) 
                if score > 0:
                    return True
        for r in range(BOARD_SIZE - 1):
            for c in range(BOARD_SIZE):
                m = Move(r, c, r + 1, c)
                temp_board = copy.deepcopy(self.board)
                self.move(m, temp_board)
                score, rem = self.check_matches(temp_board) 
                if score > 0:
                    return True
        return False


    def check_matches(self, board):
        rem = set()
        down_score = np.zeros((BOARD_SIZE, BOARD_SIZE))
        right_score = np.zeros((BOARD_SIZE, BOARD_SIZE))
        for r in range(BOARD_SIZE):
            for c in range(2, BOARD_SIZE):
                if board[r][c] == board[r][c - 1] and board[r][c] == board[r][c - 2]:
                    rem.add((r, c))
                    rem.add((r, c - 1))
                    rem.add((r, c - 2))
                    right_score[r][c] = right_score[r][c - 1] + 1

        for r in range(2, BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == board[r - 1][c] and board[r][c] == board[r - 2][c]:
                    rem.add((r, c))
                    rem.add((r - 1, c))
                    rem.add((r - 2, c))
                    down_score[r][c] = down_score[r - 1][c] + 1

        score = np.sum(right_score * 10) + np.sum (down_score * 10)

        return score, rem


    def move(self, m, board = None):
        if not board: board = self.board
        temp_gem = board[m.r0][m.c0]
        board[m.r0][m.c0] = board[m.r1][m.c1]
        board[m.r1][m.c1] = temp_gem


    def fill_empty(self):
        for r in range(BOARD_SIZE - 1, -1, -1):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == None:
                    self.board[r][c] = self.fill(r, c)


    def fill(self, r, c):
        if r == 0:
            return self.new_gem(r, c)
        if self.board[r - 1][c] == None: 
            # grab gem above recursively
            return self.fill(r - 1, c)
        else:
            color =  self.board[r - 1][c]
            self.board[r - 1][c] = None
            return color


    def update(self, surface):
        if not self.possible_moves():
            self.new_board() # no possible moves triggers a board reset

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                try:
                    color = COLORS[self.board[r][c]]    
                except: # no color = no gem
                    color = (0, 0, 0)
                rect = (c * CELL_SIZE, (r + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, color, rect)

        if self.selected:
            rect = (self.selected[1] * CELL_SIZE, self.selected[0] * CELL_SIZE + Y_OFFSET, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, (0,0,0), rect, 4)

        self.clock.tick()
        if self.timer > 0:
            self.timer -= self.clock.get_time()

        score, rem = self.check_matches(self.board) 
        if score > 0:
            if self.timer <= 0 and self.accepting_input:
                self.timer = WAIT_TIME
                self.score += score
                self.accepting_input = False
            elif self.timer <= 0 and not self.accepting_input:
                for gem in rem:
                    self.board[gem[0]][gem[1]] = None
                self.fill_empty()
                self.accepting_input = True
            else:
                for gem in rem:
                    start0 = (gem[1] * CELL_SIZE , gem[0] * CELL_SIZE + CELL_SIZE)
                    end0 = ((gem[1] + 1) * CELL_SIZE, (gem[0] + 1) * CELL_SIZE + CELL_SIZE)
                    start1 = ((gem[1] + 1) * CELL_SIZE , gem[0] * CELL_SIZE + CELL_SIZE)
                    end1 = ((gem[1]) * CELL_SIZE, (gem[0] + 1) * CELL_SIZE + CELL_SIZE)
                    pygame.draw.aaline(surface, (0,0,0), start0, end0) 
                    pygame.draw.aaline(surface, (0,0,0), start1, end1) 


    def click(self, x, y):
        if not self.accepting_input: return False

        r0 = (y - Y_OFFSET) // CELL_SIZE
        c0 = x // CELL_SIZE
        if y > Y_OFFSET:
            if self.selected == None:
                self.selected = (r0, c0)
            else:
                r1, c1 = self.selected[0], self.selected[1]
                if (r0, c0) == (r1, c1):
                    pass
                elif not abs(r1 - r0) + abs(c1 - c0) == 1: # Is not adjacent
                    pass
                else:
                    m = Move(r0, c0, r1, c1)
                    temp_board = copy.deepcopy(self.board)
                    self.move(m, temp_board)
                    score, rem = self.check_matches(temp_board) 
                    if score > 0:
                        self.move(m, self.board)

                self.selected = None



if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 36)

    game = Game()

    w = BOARD_SIZE * CELL_SIZE
    h = (BOARD_SIZE + 1) * CELL_SIZE

    windowSurface = pygame.display.set_mode((w, h), 1, 32)
    pygame.display.set_caption('Match 3')
    game.update(windowSurface)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                game.click(x, y)

        windowSurface.fill((0,0,0))        
        game.update(windowSurface)
            
        text = font.render(str(int(game.score)), True, (255,255,255))
        text_rect = text.get_rect()
        text_rect.centery = CELL_SIZE / 2
        text_rect.right = CELL_SIZE * BOARD_SIZE - CELL_SIZE / 4
        windowSurface.blit(text, text_rect)
        pygame.display.update()
