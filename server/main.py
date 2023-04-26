import socket
import time

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10111))
main_socket.setblocking(1)
main_socket.listen(10)

data = ''
continue_capture_0 = 0
continue_capture_1 = 0
players_sockets = []
players_ids = 0
first_player = True

while True:
    try:
        new_socket, addr = main_socket.accept()
        print('Connected ', addr)

        new_socket.setblocking(1)
        players_sockets.append((new_socket, players_ids))

        new_socket.send(str(players_ids).encode())
        new_socket.send(str(int(first_player)).encode())
        first_player = not first_player

        players_ids += 1
    except:
        pass
        # print('No new connections')

    if len(players_sockets) == 2:
        break

players_sockets[0][0].send(b'Start')
players_sockets[1][0].send(b'Start')

players_sockets[0][0].send(b'Go')
# players_sockets[1][0].send(b'Wait')
time.sleep(0.5)
players_sockets[0][0].send(b'[[100(0, 0), 000(None, None), 100(0, 2), 000(None, None), 100(0, 4), 000(None, None), '
                           b'100(0, 6), 000(None, None)], [000(None, None), 100(1, 1), 000(None, None), 100(1, 3), '
                           b'000(None, None), 100(1, 5), 000(None, None), 100(1, 7)], [100(2, 0), 000(None, None), '
                           b'100(2, 2), 000(None, None), 100(2, 4), 000(None, None), 100(2, 6), 000(None, None)], '
                           b'[000(None, None), 000(None, None), 000(None, None), 000(None, None), 000(None, None), '
                           b'000(None, None), 000(None, None), 000(None, None)], [000(None, None), 000(None, None), '
                           b'000(None, None), 000(None, None), 000(None, None), 000(None, None), 000(None, None), '
                           b'000(None, None)], [000(None, None), 010(5, 1), 000(None, None), 010(5, 3), 000(None, '
                           b'None), 010(5, 5), 000(None, None), 010(5, 7)], [010(6, 0), 000(None, None), 010(6, 2), '
                           b'000(None, None), 010(6, 4), 000(None, None), 010(6, 6), 000(None, None)], [000(None, '
                           b'None), 010(7, 1), 000(None, None), 010(7, 3), 000(None, None), 010(7, 5), 000(None, '
                           b'None), 010(7, 7)]]')

while True:
    if not continue_capture_1:
        try:
            continue_capture_0 = int(players_sockets[0][0].recv(5).decode())
            data = players_sockets[0][0].recv(2000).decode()
            print('continue 0: ', continue_capture_0)
            print('Received from 0: ', data)

            if continue_capture_0:
                print('Not capt 1, continuing with 0')

                players_sockets[0][0].send(b'Next')
                players_sockets[1][0].send(b'Wait')

                time.sleep(0.5)

                # players_sockets[0][0].send(data.encode())
                players_sockets[1][0].send(data.encode())
            else:
                players_sockets[1][0].send(b'Go')
                time.sleep(0.5)
                players_sockets[1][0].send(data.encode())

        except:
            pass

    if data.find('End') != -1:
        break

    if not continue_capture_0:
        try:
            continue_capture_1 = int(players_sockets[1][0].recv(5).decode())
            data = players_sockets[1][0].recv(2000).decode()
            print('continue 1: ', continue_capture_1)
            print('Received from 1: ', data)

            if continue_capture_1:
                print('Not capt 0, continuing with 1')

                players_sockets[0][0].send(b'Wait')
                players_sockets[1][0].send(b'Next')
                time.sleep(0.5)
                players_sockets[0][0].send(data.encode())
                # players_sockets[1][0].send(data.encode())
            else:
                players_sockets[0][0].send(b'Go')
                time.sleep(0.5)
                players_sockets[0][0].send(data.encode())

        except:
            pass

    if data.find('End') != -1:
        break

time.sleep(1)

for sock in players_sockets:
    sock[0].close()
main_socket.close()
