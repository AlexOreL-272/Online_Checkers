import sys
import pygame
import re
from src.globals import Globals


class Piece:
    def __init__(self, pos, enemy, role_in_game, queen=False):
        self.is_enemy = enemy
        self.is_queen = queen
        self.role_in_game = role_in_game
        self.color = Globals.pieces_colors[role_in_game]
        self.pos = pos

    def __bool__(self):
        return self.pos[0] is not None

    def __repr__(self):
        return f'{int(self.is_enemy)}{int(self.role_in_game)}{int(self.is_queen)}{self.pos}'

    @staticmethod
    def from_str(data):
        if data.find('None') == -1:
            return Piece((7 - int(data[4]), 7 - int(data[7])), 1 - int(data[0]), int(data[1]), int(data[2]))
        else:
            return Piece((None, None), 1 - int(data[0]), int(data[1]), int(data[2]))


class Checkers:
    def __init__(self, whoami):
        self.turn = False  # False for me, True for enemy
        self.capture_series = False

        self.selected = [None, None]
        self.board = [None] * 8
        for i in range(8):
            self.board[i] = [Piece((None, None), False, False)] * 8

        # self.board[3][4] = Piece((3, 4), True)
        # self.board[1][4] = Piece((1, 4), False)

        # self.board[4][3] = Piece((4, 3), False)

        # self.board[2][3] = Piece((2, 3), True)
        # self.board[3][6] = Piece((3, 6), True)
        # self.board[4][1] = Piece((4, 1), True)
        # self.board[5][4] = Piece((5, 4), True)
        # self.board[6][5] = Piece((6, 5), True)
        # self.board[6][1] = Piece((6, 1), True)

        for i in range(8):
            if i % 2:
                self.board[1][i] = Piece((1, i), True, not whoami)
                self.board[5][i] = Piece((5, i), False, whoami)
                self.board[7][i] = Piece((7, i), False, whoami)
            else:
                self.board[0][i] = Piece((0, i), True, not whoami)
                self.board[2][i] = Piece((2, i), True, not whoami)
                self.board[6][i] = Piece((6, i), False, whoami)

    def __repr__(self):
        result = ''
        for i in range(8):
            for j in range(8):
                result += str(self.board[i][j])
        return result

    def init_board_from_str(self, data):
        if not data:
            return

        new_board = re.findall('(\d{3}\((\d|None), (\d|None)\))', data)

        # print('new board: ', new_board, len(new_board))

        for i in range(8):
            for j in range(8):
                # print(new_board[63 - (i * 8 + j)][0])
                self.board[i][j] = Piece.from_str(new_board[63 - (i * 8 + j)][0])

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                if self.selected[0] == row and self.selected[1] == col:
                    pygame.draw.rect(Globals.win, Globals.selected_color,
                                     (col * Globals.square_size, row * Globals.square_size,
                                      Globals.square_size, Globals.square_size))
                    continue

                pygame.draw.rect(Globals.win, Globals.board_colors[row % 2 == col % 2],
                                 (col * Globals.square_size, row * Globals.square_size,
                                  Globals.square_size, Globals.square_size))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                current_piece = self.board[row][col]
                if current_piece:
                    self.draw_circle(current_piece.color, (col + 0.5, row + 0.5), Globals.radius)

                    if current_piece.is_queen:
                        self.draw_circle(Globals.queen_color, (col + 0.5, row + 0.5), Globals.point_radius)

    @staticmethod
    def draw_circle(color, pos, radius):
        pygame.draw.circle(Globals.win, color, (pos[0] * Globals.square_size, pos[1] * Globals.square_size), radius)

    # TODO: refactor size
    def show_available_moves(self):
        if self.selected[0] is not None:
            moves = self.possible_moves(self.selected)
            for move in moves:
                self.draw_circle(Globals.selected_color, (move[0] + 0.5, move[1] + 0.5), Globals.point_radius)

    def show_available_captures(self):
        if self.selected[0] is not None:
            moves = self.possible_captures(self.selected)
            for move in moves:
                self.draw_circle(Globals.capt_color, (move[0] + 0.5, move[1] + 0.5), Globals.point_radius)

    @staticmethod
    def __in_bounds__(pos):
        return (0 <= pos[0] <= 7) and (0 <= pos[1] <= 7)

    def is_single(self, pos, direction):
        return self.board[pos[0] + direction[0]][pos[1] + direction[1]] and \
               self.board[pos[0] + direction[0]][pos[1] + direction[1]].is_enemy and \
               not self.board[pos[0] + 2 * direction[0]][pos[1] + 2 * direction[1]]

    def two_in_row(self, pos, direction):
        return self.__in_bounds__((pos[0] + 2 * direction[0], pos[1] + 2 * direction[1])) and \
               self.board[pos[0] + direction[0]][pos[1] + direction[1]] and \
               self.board[pos[0] + 2 * direction[0]][pos[1] + 2 * direction[1]]

    def check_single_capture(self, pos, num, direction):
        return self.__in_bounds__((pos[0] + num * direction[0], pos[1] + num * direction[1])) and \
               self.is_single((pos[0] + (num - 2) * direction[0], pos[1] + (num - 2) * direction[1]), direction)

    def check_ally(self, pos):
        return self.__in_bounds__(pos) and self.board[pos[0]][pos[1]] and \
               not self.board[pos[0]][pos[1]].is_enemy

    # TODO: refactor ifs
    def possible_captures(self, pos):
        moves = []
        flags = [True] * 4

        for i in range(2, 7):
            if i == 3 and not self.board[pos[0]][pos[1]].is_queen:
                break

            # for side in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            #     if flags[]

            if flags[0] and self.check_single_capture(pos, i, (-1, -1)):
                moves.append((pos[1] - i, pos[0] - i))
                flags[0] = False
            elif self.two_in_row((pos[0] - i + 2, pos[1] - i + 2), (-1, -1)) or \
                    self.check_ally((pos[0] - i + 1, pos[1] - i + 1)):
                flags[0] = False

            if flags[1] and self.check_single_capture(pos, i, (1, -1)):
                moves.append((pos[1] - i, pos[0] + i))
                flags[1] = False
            elif self.two_in_row((pos[0] + i - 2, pos[1] - i + 2), (1, -1)) or \
                    self.check_ally((pos[0] + i - 1, pos[1] - i + 1)):
                flags[1] = False

            if flags[2] and self.check_single_capture(pos, i, (1, 1)):
                moves.append((pos[1] + i, pos[0] + i))
                flags[2] = False
            elif self.two_in_row((pos[0] + i - 2, pos[1] + i - 2), (1, 1)) or \
                    self.check_ally((pos[0] + i - 1, pos[1] + i - 1)):
                flags[2] = False

            if flags[3] and self.check_single_capture(pos, i, (-1, 1)):
                moves.append((pos[1] + i, pos[0] - i))
                flags[3] = False
            elif self.two_in_row((pos[0] - i + 2, pos[1] + i - 2), (-1, 1)) or \
                    self.check_ally((pos[0] - i + 1, pos[1] + i - 1)):
                flags[3] = False

        return moves

    # TODO: refactor ifs
    def possible_moves(self, pos):
        moves = []

        if self.check_move((pos[0] - 1, pos[1] - 1)):
            moves.append((pos[1] - 1, pos[0] - 1))

        if self.check_move((pos[0] - 1, pos[1] + 1)):
            moves.append((pos[1] + 1, pos[0] - 1))

        if self.board[pos[0]][pos[1]].is_queen:
            flags = [True] * 4
            for i in range(1, 8):
                if flags[0] and self.check_move((pos[0] - i, pos[1] - i)):
                    moves.append((pos[1] - i, pos[0] - i))
                else:
                    flags[0] = False

                if flags[1] and self.check_move((pos[0] - i, pos[1] + i)):
                    moves.append((pos[1] + i, pos[0] - i))
                else:
                    flags[1] = False

                if flags[2] and self.check_move((pos[0] + i, pos[1] + i)):
                    moves.append((pos[1] + i, pos[0] + i))
                else:
                    flags[2] = False

                if flags[3] and self.check_move((pos[0] + i, pos[1] - i)):
                    moves.append((pos[1] - i, pos[0] + i))
                else:
                    flags[3] = False

        return moves

    # TODO: capture piece
    def check_move(self, pos):
        return self.__in_bounds__(pos) and not self.board[pos[0]][pos[1]]

    def move_piece(self, new_pos):
        possible_moves = self.possible_moves(self.selected)
        possible_capts = self.possible_captures(self.selected)

        current_piece = self.board[self.selected[0]][self.selected[1]]

        if new_pos[::-1] in possible_moves:
            self.board[new_pos[0]][new_pos[1]] = Piece(new_pos, False, current_piece.role_in_game,
                                                       current_piece.is_queen)
            self.board[self.selected[0]][self.selected[1]] = Piece((None, None), False, False)
            self.selected = [None, None]

            self.turn = not self.turn
            self.capture_series = False

            if new_pos[0] == 0:
                self.board[new_pos[0]][new_pos[1]].is_queen = True

            return Globals.move_ids['moved']
        elif new_pos[::-1] in possible_capts:
            dx, dy = (self.selected[0] - new_pos[0]) > 0, (self.selected[1] - new_pos[1]) > 0

            self.board[new_pos[0]][new_pos[1]] = Piece(new_pos, False, current_piece.role_in_game,
                                                       current_piece.is_queen)
            self.board[self.selected[0]][self.selected[1]] = Piece((None, None), False, False)
            self.board[new_pos[0] + 2 * dx - 1][new_pos[1] + 2 * dy - 1] = Piece((None, None), False, False)

            if new_pos[0] == 0:
                self.board[new_pos[0]][new_pos[1]].is_queen = True

            if self.possible_captures(new_pos):
                self.selected = new_pos
                self.capture_series = True
                return Globals.move_ids['continue_capt']
            else:
                self.selected = [None, None]
                self.turn = not self.turn
                self.capture_series = False
                return Globals.move_ids['captured_one']

        return Globals.move_ids["couldn't"]
