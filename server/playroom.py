class Player:
    """
    Class of a checkers player
    """

    def __init__(self, nickname, socket, address):
        """
        :param nickname: player's nickname
        :param socket: socket to send info to
        :param address: player's web address

        Constructs a player
        """

        self.nick = nickname
        self.sock = socket
        self.addr = address

    def __repr__(self):
        """
        Casts a Player object to a string
        """
        return f'{self.nick} : {self.addr}'


class Room:
    """
    Class of a playing room
    """

    def __init__(self):
        """
        Constructs a playing room with two players in it
        """

        self.available = True
        self.first_pl = None
        self.second_pl = None
        self.capture_series_fir = 0
        self.capture_series_sec = 0

    def add_fir_player(self, player):
        """
        :param player: player to add

        Adds the first player to the room
        """

        self.first_pl = player

    def add_sec_player(self, player):
        """
        :param player: player to add

        Adds the second player to the room
        """

        self.second_pl = player
        self.available = False

    def empty(self):
        """
        Clears the playing room
        """

        self.first_pl.sock.close()
        self.second_pl.sock.close()
        self.first_pl = None
        self.second_pl = None
        self.available = True

    def __len__(self):
        """
        Returns the amount of players in the room
        """

        return self.first_pl is not None

    def __repr__(self):
        """
        Casts the room info into string
        """

        return f'{str(self.first_pl)}\n{str(self.second_pl)}\n => {self.capture_series_fir} : {self.capture_series_sec}'

