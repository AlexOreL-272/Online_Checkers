import sys
import pygame
from pygame.color import THECOLORS
pygame.init()
pygame.display.set_caption('Checkers')


class Globals:
    width = 800
    height = 800
    win = pygame.display.set_mode((width, height))
    square_size = width // 8

    radius = square_size * 3 // 8
    point_radius = square_size // 10

    board_colors = [THECOLORS['white'], THECOLORS['black']]
    selected_color = THECOLORS['purple']
    capt_color = THECOLORS['darkorange']
    pieces_colors = [None, THECOLORS['gold'], THECOLORS['maroon']]
    queen_color = THECOLORS['coral']

    move_ids = {"couldn't": 0, 'moved': 1, 'continue_capt': 2, 'captured_one': 3}