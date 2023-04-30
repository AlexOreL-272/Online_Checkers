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
    pygame.display.set_caption('Checkers')

    font = pygame.font.SysFont('Calibri', 32, True, False)
    large_font = pygame.font.SysFont('Calibri', 54, True, False)

    def __init__(self, whoami):
        self.screen = pygame.display.set_mode(Globals.checkers_size)

        self.turn = not whoami
        self.capture_series = False
        self.total_moves = 0

        self.selected = [None, None]
        self.board = [None] * 8
        for i in range(8):
            self.board[i] = [Piece((None, None), False, False)] * 8

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

        for i in range(8):
            for j in range(8):
                self.board[i][j] = Piece.from_str(new_board[63 - (i * 8 + j)][0])

    def draw_board(self):
        self.screen.fill(Globals.board_colors[0])

        for row in range(8):
            for col in range(8):
                if self.selected[0] == row and self.selected[1] == col:
                    pygame.draw.rect(self.screen, Globals.selected_color,
                                     (col * Globals.square_size, row * Globals.square_size,
                                      Globals.square_size, Globals.square_size))
                    continue

                pygame.draw.rect(self.screen, Globals.board_colors[row % 2 == col % 2],
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

    def draw_circle(self, color, pos, radius):
        pygame.draw.circle(self.screen, color, (pos[0] * Globals.square_size, pos[1] * Globals.square_size), radius)

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

    def check_end(self):
        ally_num = 0
        for i in range(8):
            for j in range(8):
                ally_num += (bool(self.board[i][j]) and not self.board[i][j].is_enemy)

        if ally_num == 0:
            return Globals.move_ids['lose']

        enemy_num = 0
        for i in range(8):
            for j in range(8):
                enemy_num += (bool(self.board[i][j]) and self.board[i][j].is_enemy)

        if enemy_num == 0:
            return Globals.move_ids['win']

        return Globals.move_ids['not_ended']

    @staticmethod
    def __in_bounds__(pos):
        return (0 <= pos[0] <= 7) and (0 <= pos[1] <= 7)

    def __is_single__(self, pos, direction):
        return self.board[pos[0] + direction[0]][pos[1] + direction[1]] and \
               self.board[pos[0] + direction[0]][pos[1] + direction[1]].is_enemy and \
               not self.board[pos[0] + 2 * direction[0]][pos[1] + 2 * direction[1]]

    def __two_in_row__(self, pos, direction):
        return self.__in_bounds__((pos[0] + 2 * direction[0], pos[1] + 2 * direction[1])) and \
               self.board[pos[0] + direction[0]][pos[1] + direction[1]] and \
               self.board[pos[0] + 2 * direction[0]][pos[1] + 2 * direction[1]]

    def __check_single_capture__(self, pos, num, direction):
        return self.__in_bounds__((pos[0] + num * direction[0], pos[1] + num * direction[1])) and \
               self.__is_single__((pos[0] + (num - 2) * direction[0], pos[1] + (num - 2) * direction[1]), direction)

    def __check_ally__(self, pos):
        return self.__in_bounds__(pos) and self.board[pos[0]][pos[1]] and \
               not self.board[pos[0]][pos[1]].is_enemy

    def possible_captures(self, pos):
        moves = []
        flags = [True] * 4

        for i in range(2, 7):
            if i == 3 and not self.board[pos[0]][pos[1]].is_queen:
                break

            # side[0] + (side[1] + 3) // 2 is just a function to convert directions to ints
            for side in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                idx = side[0] + (side[1] + 3) // 2
                if flags[idx] and self.__check_single_capture__(pos, i, side):
                    moves.append((pos[1] + i * side[1], pos[0] + i * side[0]))
                    flags[idx] = False
                elif self.__two_in_row__((pos[0] + (i - 2) * side[0], pos[1] + (i - 2) * side[1]), side) or \
                        self.__check_ally__((pos[0] + (i - 1) * side[0], pos[1] + (i - 1) * side[1])):
                    flags[idx] = False

        return moves

    def possible_moves(self, pos):
        moves = []

        if self.check_move((pos[0] - 1, pos[1] - 1)):
            moves.append((pos[1] - 1, pos[0] - 1))

        if self.check_move((pos[0] - 1, pos[1] + 1)):
            moves.append((pos[1] + 1, pos[0] - 1))

        if self.board[pos[0]][pos[1]].is_queen:
            flags = [True] * 4
            for i in range(1, 8):
                for side in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                    idx = side[0] + (side[1] + 3) // 2
                    if flags[idx] and self.check_move((pos[0] + i * side[0], pos[1] + i * side[1])):
                        moves.append((pos[1] + i * side[1], pos[0] + i * side[0]))
                    else:
                        flags[idx] = False

        return moves

    def check_move(self, pos):
        return self.__in_bounds__(pos) and not self.board[pos[0]][pos[1]]

    def __move_piece__(self, new_pos, current_piece):
        self.board[new_pos[0]][new_pos[1]] = Piece(new_pos, False, current_piece.role_in_game,
                                                   current_piece.is_queen)
        self.board[self.selected[0]][self.selected[1]] = Piece((None, None), False, False)
        self.selected = [None, None]

        self.turn = not self.turn
        self.capture_series = False
        self.total_moves += 1

        if new_pos[0] == 0:
            self.board[new_pos[0]][new_pos[1]].is_queen = True

        end_state = self.check_end()
        if end_state == Globals.move_ids['win'] or end_state == Globals.move_ids['lose']:
            return end_state

        return Globals.move_ids['moved']

    def __capture_piece__(self, new_pos, prev_piece):
        dx, dy = (self.selected[0] - new_pos[0]) > 0, (self.selected[1] - new_pos[1]) > 0

        self.board[new_pos[0]][new_pos[1]] = Piece(new_pos, False, prev_piece.role_in_game, prev_piece.is_queen)
        self.board[self.selected[0]][self.selected[1]] = Piece((None, None), False, False)
        self.board[new_pos[0] + 2 * dx - 1][new_pos[1] + 2 * dy - 1] = Piece((None, None), False, False)
        self.total_moves += 1

        if new_pos[0] == 0:
            self.board[new_pos[0]][new_pos[1]].is_queen = True

        end_state = self.check_end()
        if end_state == Globals.move_ids['win'] or end_state == Globals.move_ids['lose']:
            return end_state

        self.capture_series = self.possible_captures(new_pos)
        self.selected = new_pos if self.capture_series else [None, None]
        self.turn = self.turn if self.capture_series else not self.turn
        return Globals.move_ids['continue_capt'] if self.capture_series else Globals.move_ids['captured_one']

    def move_piece(self, new_pos):
        possible_moves = self.possible_moves(self.selected)
        possible_capts = self.possible_captures(self.selected)

        current_piece = self.board[self.selected[0]][self.selected[1]]

        if new_pos[::-1] in possible_moves:
            return self.__move_piece__(new_pos, current_piece)
        elif new_pos[::-1] in possible_capts:
            return self.__capture_piece__(new_pos, current_piece)

        return Globals.move_ids["couldn't"]

    def show_players(self, my_nick, enemy_nick, room_id):
        self.draw_circle(Globals.queen_color, (8.2, 0.33 if self.turn else 7.63), Globals.point_radius)

        my_nick = Checkers.font.render(my_nick, True, Globals.font_colors['Black'])
        self.screen.blit(my_nick, (840, 750))
        enemy_nick = Checkers.font.render(enemy_nick, True, Globals.font_colors['Black'])
        self.screen.blit(enemy_nick, (840, 20))
        room_id = Checkers.font.render('This room id: ' + room_id, True, Globals.font_colors['Black'])
        self.screen.blit(room_id, (1000, 750))

    def show_results(self, result, game_time):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            result_text = Checkers.large_font.render('You ' + ('win!' if not int(result) else 'lose!'), True,
                                                     Globals.font_colors['Black'])
            self.screen.blit(result_text, (880, 200))
            game_time_text = Checkers.font.render('Game took: ' + game_time[0:10], True, Globals.font_colors['Black'])
            self.screen.blit(game_time_text, (840, 400))
            total_moves_text = Checkers.font.render('You\'ve made ' + str(self.total_moves) + ' moves', True,
                                                    Globals.font_colors['Black'])
            self.screen.blit(total_moves_text, (840, 450))
            exit_text = Checkers.font.render('You can close this window', True, Globals.font_colors['Black'])
            self.screen.blit(exit_text, (840, 500))

            pygame.display.update()
