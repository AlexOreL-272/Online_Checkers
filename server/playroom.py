class Player:
    def __init__(self, nickname, socket, address):
        self.nick = nickname
        self.sock = socket
        self.addr = address

    def __repr__(self):
        return f'{self.nick} : {self.addr}'


class Room:
    def __init__(self):
        self.available = True
        self.first_pl = None
        self.second_pl = None
        self.capture_series_fir = 0
        self.capture_series_sec = 0

    def add_fir_player(self, player):
        self.first_pl = player

    def add_sec_player(self, player):
        self.second_pl = player
        self.available = False

    def empty(self):
        self.first_pl.sock.close()
        self.second_pl.sock.close()
        self.first_pl = None
        self.second_pl = None
        self.available = True

    def __len__(self):
        return self.first_pl is not None

    def __repr__(self):
        return f'{str(self.first_pl)}\n{str(self.second_pl)}\n => {self.capture_series_fir} : {self.capture_series_sec}'

