from pico2d import *

import math

open_canvas()

character = load_image('character.png')

def draw_Circle():
    print("Cirlce")

    for i in range(360):

        theta = math.radians(i)
        x = 400 + 200 * math.cos(theta)
        y = 300 + 200 * math.sin(theta)
        draw_character(x, y)

    pass
