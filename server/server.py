import socket
import time


main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10000))
main_socket.setblocking(0)
main_socket.listen(10)

data = ''
players_sockets = []
while True:
    try:
        new_socket, addr = main_socket.accept()
        print('Connected ', addr)
        new_socket.setblocking(0)
        players_sockets.append(new_socket)
    except:
        print('No new connections')


    for sock in players_sockets:
        try:
            data = sock.recv(1024).decode()
            print('Received: ', data)
        except:
            pass

    if len(players_sockets) == 2:
        for sock in players_sockets:
            try:
                sock.send('Some info...'.encode())
            except:
                players_sockets.remove(sock)
                sock.close()


    time.sleep(1)
  