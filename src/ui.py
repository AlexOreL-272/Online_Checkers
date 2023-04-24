from src.checkers import Checkers
from src.globals import Globals
import socket
import sys
import pygame


class UI:
    def __init__(self):
        self.game = Checkers()
        self.game.draw_board()
        self.game.draw_pieces()
        pygame.display.update()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect(('localhost', 10000))

    def mainloop(self):
        while True:
            data = self.sock.recv(1024).decode()

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    y_pos, x_pos = pygame.mouse.get_pos()
                    x_pos, y_pos = x_pos // Globals.square_size, y_pos // Globals.square_size

                    if self.game.selected[0] is None and self.game.board[x_pos][y_pos] and \
                            not self.game.board[x_pos][y_pos].is_enemy:
                        self.game.selected = [x_pos, y_pos]
                    elif not self.game.capture_series and x_pos == self.game.selected[0] and y_pos == self.game.selected[1]:
                        self.game.selected = [None, None]
                    elif self.game.selected[0] is not None:
                        result = self.game.move_piece((x_pos, y_pos))
                        if result == Globals.move_ids['continue_capt']:
                            pass

                    self.game.draw_board()
                    self.game.draw_pieces()
                    self.game.show_available_moves()
                    self.game.show_available_captures()
                    pygame.display.update()
