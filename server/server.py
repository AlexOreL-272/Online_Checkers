import socket
import time
import playroom
import traceback


class Server:
    def __init__(self):
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.main_socket.bind(('localhost', 10111))
        self.main_socket.setblocking(0)
        self.main_socket.listen(10)

        self.authorizing_players = []
        self.playing_rooms = []

        self.first_player = True
        self.next_pl_id = 0

    @staticmethod
    def send_init_data(room):
        room.first_pl.sock.send(f'{room.second_pl.nick}'.encode())
        room.second_pl.sock.send(f'{room.first_pl.nick}'.encode())
        time.sleep(0.05)
        room.first_pl.sock.send(
            b'Move[[110(0, 0), 000(None, None), 110(0, 2), 000(None, None), 110(0, 4), 000(None, None), '
            b'110(0, 6), 000(None, None)], [000(None, None), 110(1, 1), 000(None, None), 110(1, 3), '
            b'000(None, None), 110(1, 5), 000(None, None), 110(1, 7)], [110(2, 0), 000(None, None), '
            b'110(2, 2), 000(None, None), 110(2, 4), 000(None, None), 110(2, 6), 000(None, None)], '
            b'[000(None, None), 000(None, None), 000(None, None), 000(None, None), 000(None, None), '
            b'000(None, None), 000(None, None), 000(None, None)], [000(None, None), 000(None, None), '
            b'000(None, None), 000(None, None), 000(None, None), 000(None, None), 000(None, None), '
            b'000(None, None)], [000(None, None), 000(5, 1), 000(None, None), 000(5, 3), 000(None, '
            b'None), 000(5, 5), 000(None, None), 000(5, 7)], [000(6, 0), 000(None, None), 000(6, 2), '
            b'000(None, None), 000(6, 4), 000(None, None), 000(6, 6), 000(None, None)], [000(None, '
            b'None), 000(7, 1), 000(None, None), 000(7, 3), 000(None, None), 000(7, 5), 000(None, '
            b'None), 000(7, 7)]]'
        )

    def try_accept_player(self):
        try:
            new_socket, addr = self.main_socket.accept()
            print(f'Connected {addr}')

            new_socket.setblocking(0)
            self.authorizing_players.append((new_socket, addr))

            new_socket.send(str(self.next_pl_id).encode())
            new_socket.send(str(int(self.first_player)).encode())
            self.first_player = not self.first_player

            self.next_pl_id += 1
        except:
            pass

    def try_register_player(self):
        for player in self.authorizing_players:
            try:
                action, nick, room_id = player[0].recv(100).decode().split(':')

                if action == 'new':
                    self.playing_rooms.append(playroom.Room())
                    self.playing_rooms[-1].add_fir_player(playroom.Player(nick, player[0], player[1]))
                    player[0].send(f'{len(self.playing_rooms) - 1}'.encode())
                    print(f'Player {nick} created room {len(self.playing_rooms) - 1}')
                else:
                    room_id = int(room_id)
                    this_room = self.playing_rooms[room_id]
                    if this_room.available:
                        if len(this_room):
                            this_room.add_sec_player(playroom.Player(nick, player[0], player[1]))
                        else:
                            this_room.add_fir_player(playroom.Player(nick, player[0], player[1]))
                        self.send_init_data(this_room)
                        print(f'Player {nick} has joined room {room_id}')

                self.authorizing_players.remove(player)
            except:
                pass

    @staticmethod
    def try_receive_game_from_first(room):
        try:
            data = room.first_pl.sock.recv(2000).decode()
            room.capture_series_fir = int(data[0])

            if room.capture_series_fir == 1:
                room.first_pl.sock.send(b'Next')
                room.second_pl.sock.send(f'Wait{data[1:]}'.encode())
            elif room.capture_series_fir == 0:
                room.second_pl.sock.send(f'Move{data[1:]}'.encode())
            else:   # received 3{0|1}[board]
                game_result = int(data[1])
                room.first_pl.sock.send(f'Stop2{game_result}'.encode())
                room.second_pl.sock.send(f'Stop0{1 - game_result}{data[2:]}'.encode())
                return True
        except:
            pass

    @staticmethod
    def try_receive_game_from_second(room):
        try:
            data = room.second_pl.sock.recv(2000).decode()
            room.capture_series_sec = int(data[0])

            if room.capture_series_sec == 1:
                room.second_pl.sock.send(b'Next')
                room.first_pl.sock.send(f'Wait{data[1:]}'.encode())
            elif room.capture_series_sec == 0:
                room.first_pl.sock.send(f'Move{data[1:]}'.encode())
            else:
                game_result = int(data[1])
                room.first_pl.sock.send(f'Stop0{1 - game_result}{data[2:]}'.encode())
                room.second_pl.sock.send(f'Stop2{game_result}'.encode())
                return True
        except:
            pass

    def mainloop(self):
        while True:
            self.try_accept_player()
            self.try_register_player()

            for room in self.playing_rooms:
                if room.second_pl is None:
                    continue

                if not room.capture_series_sec:
                    if self.try_receive_game_from_first(room) is not None:
                        room.empty()

                if not room.capture_series_fir:
                    if self.try_receive_game_from_second(room) is not None:
                        room.empty()
