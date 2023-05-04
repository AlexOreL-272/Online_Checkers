import datetime
import pygame
from src.authorization import Auth
from src.checkers import Checkers
from src.globals import Globals
import socket
import sys
import time


class UI:
    """
    Class of the user interface
    """

    def __init__(self):
        """
        Constructs the UI
        """

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect(('localhost', 10111))
        self.serial_id = self.sock.recv(10).decode()
        self.whoami = self.sock.recv(1).decode()

        self.auth = Auth()
        self.auth.show_login_form()
        action = self.auth.main_menu()
        self.sock.send(f'{action}:{self.auth.login}:{self.auth.room_id}'.encode())
        self.room_id = self.auth.room_id if action == 'join' else self.sock.recv(10).decode()
        self.my_nick = self.auth.login
        self.enemy_nick = ''
        self.auth.close()

        self.game = Checkers(int(self.whoami))
        self.update_screen()

    def update_screen(self, show_moves=False):
        """
        :param show_moves: flag if the moves need to be showed

        Updates current game state
        """

        self.game.draw_board()
        self.game.draw_pieces()
        self.game.show_players(self.my_nick, self.enemy_nick, self.room_id)

        if show_moves and self.game.selected[0] is not None:
            self.game.show_available_moves()
            self.game.show_available_captures()

        pygame.display.update()

    def perform_action(self, starttime):
        """
        :param starttime: starting time of the game

        Receives the action from the server and acts accordingly
        """

        data = self.sock.recv(2000).decode()

        action = data[0:4]
        if action != 'Next':
            if action != 'Stop' or data[4] != '2':
                self.game.init_board_from_str(data)

            if action == 'Stop':
                self.sock.close()
                self.update_screen()
                self.game.show_results(data[5], str(datetime.timedelta(seconds=time.time() - starttime)))

            if action == 'Move':
                self.game.turn = False

            if action == 'Wait':
                return True

        self.update_screen(True)
        return False

    def mouse_clicked(self):
        """
        Performs the action according to mouse event
        """

        y_pos, x_pos = pygame.mouse.get_pos()
        if y_pos >= Globals.checkers_size[1]:
            return False

        x_pos, y_pos = x_pos // Globals.square_size, y_pos // Globals.square_size
        if self.game.selected[0] is None and self.game.board[x_pos][y_pos] and \
                not self.game.board[x_pos][y_pos].is_enemy:
            self.game.selected = [x_pos, y_pos]
        elif not self.game.capture_series and x_pos == self.game.selected[0] and y_pos == self.game.selected[1]:
            self.game.selected = [None, None]
        elif self.game.selected[0] is not None:
            result = self.game.move_piece((x_pos, y_pos))

            if result == Globals.move_ids['win'] or result == Globals.move_ids['lose']:
                self.sock.send(f'3{result}{str(self.game.board)}'.encode())
                return True

            if result != Globals.move_ids["couldn't"]:
                can_continue = int(result == Globals.move_ids['continue_capt'])
                self.sock.send(f'{can_continue}{str(self.game.board)}'.encode())
                return True

        return False

    def mainloop(self):
        """
        Main loop of the game
        """

        self.enemy_nick = self.sock.recv(15).decode()
        self.update_screen()
        starttime = time.time()

        while True:
            if self.perform_action(starttime):
                continue

            move_flag = False
            while True:
                if move_flag:
                    break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.sock.send(f'30{self.game.board}'.encode())
                        move_flag = True
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        move_flag = self.mouse_clicked()

                self.update_screen(True)
