import pygame
from pygame.color import THECOLORS


class Globals:
    checkers_size = (800, 800)
    auth_size = (400, 220)
    square_size = checkers_size[0] // 8

    radius = square_size * 3 // 8
    point_radius = square_size // 10

    board_colors = [THECOLORS['white'], THECOLORS['black']]
    selected_color = THECOLORS['purple']
    capt_color = THECOLORS['darkorange']
    pieces_colors = [THECOLORS['gold'], THECOLORS['maroon']]
    queen_color = THECOLORS['coral']

    auth_colors = {'Black': THECOLORS['black'], 'White': THECOLORS['white'], 'Blue': THECOLORS['blue'],
                   'Green': THECOLORS['green'], 'Red': THECOLORS['red']}

    move_ids = {"couldn't": 0, 'moved': 1, 'continue_capt': 2, 'captured_one': 3, 'win': 4, 'lose': 5, 'not_ended': 6}
    # choice_ids = {'new': 0, 'join': 1}
