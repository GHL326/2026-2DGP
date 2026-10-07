from pathlib import Path
from pico2d import *


WIDTH, HEIGHT = 800, 600
ASSET_DIR = Path(__file__).resolve().parent

open_canvas(WIDTH, HEIGHT)
hide_cursor()
character = load_image(str(ASSET_DIR / 'animation_sheet.png'))

running = True
frame = 0
x, y = WIDTH // 2, HEIGHT // 2


def handle_events():
    global running, x, y

    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and getattr(event, 'key', None) == SDLK_ESCAPE:
            running = False
        elif event.type == SDL_MOUSEMOTION:
            x = event.x
            y = HEIGHT - 1 - event.y


try:
    while running:
        handle_events()
        if not running:
            break

        clear_canvas()
        character.clip_draw(frame * 100, 100, 100, 100, x, y)
        update_canvas()
        frame = (frame + 1) % 8
        delay(0.05)
finally:
    show_cursor()
    close_canvas()
