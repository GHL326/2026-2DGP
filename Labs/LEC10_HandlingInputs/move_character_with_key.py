from pathlib import Path
from pico2d import *


WIDTH, HEIGHT = 800, 600
RUN_LEFT, RUN_RIGHT = 0, 1
IDLE_LEFT, IDLE_RIGHT = 2, 3
ASSET_DIR = Path(__file__).resolve().parent

open_canvas(WIDTH, HEIGHT)
grass = load_image(str(ASSET_DIR / 'grass.png'))
character = load_image(str(ASSET_DIR / 'animation_sheet.png'))

running = True
x = WIDTH // 2
frame = 0
direction = 0
facing = 1
action = IDLE_RIGHT
pressed_keys = set()


def handle_events():
    global running, direction

    for event in get_events():
        key = getattr(event, 'key', None)
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if key == SDLK_ESCAPE:
                running = False
            elif key in (SDLK_LEFT, SDLK_RIGHT):
                pressed_keys.add(key)
        elif event.type == SDL_KEYUP:
            pressed_keys.discard(key)

    direction = int(SDLK_RIGHT in pressed_keys) - int(SDLK_LEFT in pressed_keys)


try:
    while running:
        handle_events()
        if not running:
            break

        x = clamp(50, x + direction * 5, WIDTH - 50)
        if direction:
            facing = direction
            next_action = RUN_RIGHT if direction > 0 else RUN_LEFT
        else:
            next_action = IDLE_RIGHT if facing > 0 else IDLE_LEFT
        if next_action != action:
            frame = 0
        action = next_action

        clear_canvas()
        grass.draw(WIDTH // 2, 30)
        character.clip_draw(frame * 100, action * 100, 100, 100, x, 90)
        update_canvas()
        frame = (frame + 1) % 8
        delay(0.05)
finally:
    close_canvas()
