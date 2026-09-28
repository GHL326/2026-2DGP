from pico2d import *

import math
from pathlib import Path
from time import perf_counter


WIDTH, HEIGHT = 800, 600
SPEED = 220.0  # Pixels per second.
CIRCLE_RADIUS = 200.0
RECTANGLE = ((80, 520), (720, 520), (720, 80), (80, 80))


def polygon_position(vertices, distance):
    edges = list(zip(vertices, vertices[1:] + vertices[:1]))
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in edges]
    remaining = distance % sum(lengths)

    for (start, end), length in zip(edges, lengths):
        if remaining < length:
            ratio = remaining / length
            return (
                start[0] + (end[0] - start[0]) * ratio,
                start[1] + (end[1] - start[1]) * ratio,
            )
        remaining -= length
    return vertices[0]


def circle_position(distance):
    angle = (distance % (math.tau * CIRCLE_RADIUS)) / CIRCLE_RADIUS
    return (
        WIDTH / 2 + CIRCLE_RADIUS * math.cos(angle),
        HEIGHT / 2 + CIRCLE_RADIUS * math.sin(angle),
    )


def position_for(motion, distance):
    if motion == 'circle':
        return circle_position(distance)
    if motion == 'rectangle':
        return polygon_position(RECTANGLE, distance)
    return WIDTH / 2, HEIGHT / 2


def main():
    open_canvas(WIDTH, HEIGHT)
    try:
        image_path = Path(__file__).resolve().with_name('character.png')
        if not image_path.is_file():
            image_path = Path(__file__).resolve().parents[2] / 'LEC05' / 'character.png'
        character = load_image(str(image_path))

        motion = 'circle'
        distance = 0.0
        running = True
        last_time = perf_counter()
        keys = {SDLK_t: 'triangle', SDLK_r: 'rectangle', SDLK_c: 'circle'}
        print('T: triangle | R: rectangle | C: circle | ESC: quit')

        while running:
            now = perf_counter()
            elapsed = min(now - last_time, 0.1)
            last_time = now

            for event in get_events():
                if event.type == SDL_QUIT:
                    running = False
                elif event.type == SDL_KEYDOWN:
                    if event.key == SDLK_ESCAPE:
                        running = False
                    elif event.key in keys and keys[event.key] != motion:
                        motion = keys[event.key]
                        distance = 0.0

            if not running:
                break

            x, y = position_for(motion, distance)
            clear_canvas()
            character.draw(x, y)
            update_canvas()
            distance += SPEED * elapsed
            delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
