from pico2d import *

import math
from pathlib import Path

open_canvas()

character = load_image(str(Path(__file__).resolve().parent / 'character.png'))
running = True

def draw_Circle():
    global running
    print("Cirlce")

    for i in range(360):

        theta = math.radians(i)
        x = 400 + 200 * math.cos(theta)
        y = 300 + 200 * math.sin(theta)
        draw_character(x, y)

    pass

def draw_Rectangle():
    print("Rectangle")
    pass

def draw_character(x, y):
    clear_canvas()
    character.draw(x , y)
    update_canvas()
    delay(0.05)

while running:
    draw_Circle()
    if not running:
        break
    draw_Rectangle()

close_canvas()
