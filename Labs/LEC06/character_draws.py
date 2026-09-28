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
    move_top()
    move_right()
    pass

def draw_character(x, y):
    clear_canvas()
    character.draw(x , y)
    update_canvas()
    delay(0.05)

def move_top():
    print("Move top")
    for x in range(50, 750, 5):
        draw_character(x, 550)

def move_right():
    print("Move right")
    for y in range(550, 50, -5):
        draw_character(750, y)
    pass

def move_left():
    print("Move left")
    for y in range(50, 550, 5):
        draw_character(50, y)
    pass

def move_bottom():
    print("Move bottom")
    for x in range(50, 750, 5):
        draw_character(x, 50)
    pass

while running:
    draw_Circle()
    if not running:
        break
    draw_Rectangle()

close_canvas()
