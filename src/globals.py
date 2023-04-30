import pygame
from pygame.color import THECOLORS


class Globals:
    checkers_size = (1200, 800)
    auth_size = (400, 220)
    square_size = checkers_size[1] // 8

    radius = square_size * 3 // 8
    point_radius = square_size // 10

    board_colors = [THECOLORS['white'], THECOLORS['black']]
    selected_color = THECOLORS['purple']
    capt_color = THECOLORS['darkorange']
    pieces_colors = [THECOLORS['gold'], THECOLORS['maroon']]
    queen_color = THECOLORS['coral']

    font_colors = {'Black': THECOLORS['black'], 'White': THECOLORS['white'], 'Blue': THECOLORS['blue'],
                   'Green': THECOLORS['green'], 'Red': THECOLORS['red']}

    move_ids = {'win': 0, 'lose': 1, "couldn't": 2, 'moved': 3, 'continue_capt': 4, 'captured_one': 5, 'not_ended': 6}
