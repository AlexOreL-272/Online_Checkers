import numpy as np

from src.checkers import Checkers
from src.globals import Globals
import socket
import sys
import pygame


class UI:
    def __init__(self):
        # self.game = Checkers(True)
        # self.game.draw_board()
        # self.game.draw_pieces()
        #
        # print(str(self.game.board))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect(('localhost', 10111))
        self.serial_id = self.sock.recv(10).decode()

        print('Serid: ', self.serial_id)

        self.whoami = self.sock.recv(1).decode()

        print('I am enemy: ', self.whoami)

        self.game = Checkers(int(self.whoami))
        self.game.draw_board()
        self.game.draw_pieces()

        pygame.display.update()

    def mainloop(self):
        data = self.sock.recv(5).decode()     # got 'Start'
        print('Received init data: ', data)
        num = 1

        while True:
            move_flag = False
            print('Waiting')
            pl_id = self.sock.recv(10).decode()

            print(f'=========== {num} {pl_id} ===========')
            num += 1

            if pl_id.find('Next') == -1:
                data = self.sock.recv(2000).decode()    # wait
                print('Received some data')
                self.game.init_board_from_str(data)
                self.game.draw_board()
                self.game.draw_pieces()
                pygame.display.update()

                if pl_id.find('Wait') != -1:
                    print('=========== Ought to wait ===========')
                    continue
                else:
                    print('=========== Waiting for move ===========')

            while True:
                if move_flag:
                    break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.sock.send('End'.encode())
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        y_pos, x_pos = pygame.mouse.get_pos()
                        x_pos, y_pos = x_pos // Globals.square_size, y_pos // Globals.square_size

                        if self.game.selected[0] is None and self.game.board[x_pos][y_pos] and \
                                not self.game.board[x_pos][y_pos].is_enemy:
                            # print(np.asarray(self.game.board))
                            # print('Pos: ', x_pos, y_pos)
                            self.game.selected = [x_pos, y_pos]
                        elif not self.game.capture_series and x_pos == self.game.selected[0] and y_pos == \
                                self.game.selected[1]:
                            self.game.selected = [None, None]
                        elif self.game.selected[0] is not None:
                            result = self.game.move_piece((x_pos, y_pos))
                            if result != Globals.move_ids["couldn't"]:
                                print('move result: ', result)
                                self.sock.send(b'1' if result == Globals.move_ids['continue_capt'] else b'0')
                                self.sock.send(str(self.game.board).encode())
                                print('Sent some data')
                                move_flag = True

                        self.game.draw_board()
                        self.game.draw_pieces()
                        self.game.show_available_moves()
                        self.game.show_available_captures()

                # self.sock.send(str(self.game.board).encode())
                    pygame.display.update()
