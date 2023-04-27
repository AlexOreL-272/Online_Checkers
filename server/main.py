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
        room.first_pl.sock.send(b'Start')
        room.second_pl.sock.send(b'Start')
        room.first_pl.sock.send(b'Go')
        time.sleep(0.05)
        room.first_pl.sock.send(
            b'[[110(0, 0), 000(None, None), 110(0, 2), 000(None, None), 110(0, 4), 000(None, None), '
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

    def mainloop(self):
        while True:
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

            for player in self.authorizing_players:
                try:
                    action, nick, room_id = player[0].recv(100).decode().split(':')

                    print(f'{action} ({action == "new"}), {nick}, {room_id}')

                    if action == 'new':
                        self.playing_rooms.append(playroom.Room(playroom.Player(nick, player[0], player[1])))
                        # player[0].send(str(len(self.playing_rooms) - 1).encode())
                        print(f'Created room {len(self.playing_rooms) - 1}')
                    else:
                        self.playing_rooms[int(room_id)].add_player(playroom.Player(nick, player[0], player[1]))
                        # player[0].send(room_id.encode())
                        self.send_init_data(self.playing_rooms[int(room_id)])
                        print(f'Player has joined room {room_id}')

                    self.authorizing_players.remove(player)
                except:
                    pass

            for room in self.playing_rooms:
                if room.second_pl is None:
                    continue
                data = ''
                if not room.capture_series_sec:
                    try:
                        data = room.first_pl.sock.recv(2000).decode()
                        room.capture_series_fir = int(data[0])
                        print('continue 0: ', room.capture_series_fir)
                        print('Received from 0: ', data)

                        if room.capture_series_fir:
                            print('Not capt 1, continuing with 0')

                            room.first_pl.sock.send(b'Next')
                            room.second_pl.sock.send(b'Wait')

                            room.second_pl.sock.send(data[1:].encode())
                        else:
                            room.second_pl.sock.send(b'Go')
                            room.second_pl.sock.send(data[1:].encode())
                    except:
                        pass

                if data.find('End') != -1:
                    room.first_pl.sock.close()
                    room.second_pl.sock.close()
                    self.playing_rooms.remove(room)
                    continue

                if not room.capture_series_fir:
                    try:
                        data = room.second_pl.sock.recv(2000).decode()
                        room.capture_series_sec = int(data[0])
                        print('continue 1: ', room.capture_series_sec)
                        print('Received from 1: ', data)

                        if room.capture_series_sec:
                            print('Not capt 0, continuing with 1')

                            room.first_pl.sock.send(b'Wait')
                            room.second_pl.sock.send(b'Next')
                            room.first_pl.sock.send(data[1:].encode())
                        else:
                            room.first_pl.sock.send(b'Go')
                            room.first_pl.sock.send(data[1:].encode())
                    except:
                        pass

                if data.find('End') != -1:
                    room.first_pl.sock.close()
                    room.second_pl.sock.close()
                    self.playing_rooms.remove(room)
                    continue


serv = Server()
serv.mainloop()


# for sock in authorizing_players:
#     sock[0].close()
# main_socket.close()
