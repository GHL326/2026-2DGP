"""Drill 8: five centered animations, five loops each, one-second holds."""
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 900, 700
SCALE = 1.35
BASELINE = 110
REPEATS = 5
PAUSE_SECONDS = 1.0


@dataclass(frozen=True)
class Frame:
    rect: tuple[int, int, int, int]
    pivot: tuple[float, float]


@dataclass(frozen=True)
class Animation:
    name: str
    fps: float
    frames: tuple[Frame, ...]


def load_animations(path=ROOT / 'animations.json'):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    animations = tuple(
        Animation(item['name'], item['fps'], tuple(
            Frame(tuple(frame['rect']), tuple(frame['pivot']))
            for frame in item['frames']
        )) for item in data['animations']
    )
    return Path(path).parent / data['image'], animations


def validate_animations(animations, image_width, image_height):
    if len(animations) < 4:
        raise ValueError('At least four animations are required')
    for animation in animations:
        if not animation.frames or not math.isfinite(animation.fps) or animation.fps <= 0:
            raise ValueError(f'Invalid animation: {animation.name}')
        for frame in animation.frames:
            x, y, w, h = frame.rect
            if min(x, y) < 0 or min(w, h) <= 0:
                raise ValueError(f'Invalid frame: {frame}')
            if x + w > image_width or y + h > image_height:
                raise ValueError(f'Frame outside sprite sheet: {frame}')


class Player:
    def __init__(self, animations):
        self.animations = animations
        self.index = 0
        self.elapsed = 0.0

    @property
    def animation(self):
        return self.animations[self.index]

    @property
    def play_seconds(self):
        return len(self.animation.frames) * REPEATS / self.animation.fps

    @property
    def holding(self):
        return self.elapsed >= self.play_seconds

    @property
    def frame_index(self):
        if self.holding:
            return len(self.animation.frames) - 1
        return int(self.elapsed * self.animation.fps) % len(self.animation.frames)

    @property
    def repeat_number(self):
        if self.holding:
            return REPEATS
        return min(REPEATS, int(self.elapsed * self.animation.fps) // len(self.animation.frames) + 1)

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def advance(self, seconds):
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError('Elapsed time must be finite and nonnegative')
        self.elapsed += seconds
        # Whole cycles have no effect, including after a long suspended window.
        cycle = sum(len(a.frames) * REPEATS / a.fps + PAUSE_SECONDS for a in self.animations)
        self.elapsed %= cycle
        while self.elapsed >= self.play_seconds + PAUSE_SECONDS:
            self.elapsed -= self.play_seconds + PAUSE_SECONDS
            self.index = (self.index + 1) % len(self.animations)


def frame_destination(frame):
    _, _, width, height = frame.rect
    pivot_x, pivot_y = frame.pivot
    return (
        WIDTH / 2 + (width / 2 - pivot_x) * SCALE,
        BASELINE + (pivot_y - height / 2) * SCALE,
        width * SCALE,
        height * SCALE,
    )


def draw_sprite(sheet, frame):
    left, top, width, height = frame.rect
    # Metadata uses a top-left origin; pico2d clipping uses bottom-left.
    sheet.clip_draw(left, sheet.h - top - height, width, height,
                    *frame_destination(frame))


def draw_background(canvas):
    canvas.clear_canvas()
    canvas.draw_rectangle(0, 0, WIDTH, HEIGHT, 21, 28, 39, filled=True)
    canvas.draw_rectangle(28, 110, WIDTH - 28, 600, 32, 44, 58, filled=True)
    canvas.draw_line(70, BASELINE - 5, WIDTH - 70, BASELINE - 5, 88, 116, 134)


def draw_status(canvas, font, player):
    if font is None:
        return
    animation = player.animation
    font.draw(32, 654, 'KNIGHT / ANIMATION VIEWER', (226, 235, 244))
    font.draw(32, 614, f'{player.index + 1:02d}  {animation.name.upper()}', (108, 219, 201))
    status = (f'HOLD  {max(0, PAUSE_SECONDS - (player.elapsed - player.play_seconds)):.1f}s'
              if player.holding else f'LOOP  {player.repeat_number} / {REPEATS}')
    font.draw(470, 614, status, (255, 203, 117))
    font.draw(40, 78, f'FRAME {player.frame_index + 1:02d}/{len(animation.frames):02d}'
              f'     {animation.fps:g} FPS     {SCALE:g}x', (182, 202, 219))
    font.draw(40, 40, 'AUTO: 5 LOOPS > 1s HOLD > NEXT     ESC: QUIT', (146, 170, 190))
    progress = min(1.0, player.elapsed / player.play_seconds)
    canvas.draw_rectangle(40, 99, WIDTH - 40, 104, 56, 73, 89, filled=True)
    canvas.draw_rectangle(40, 99, 40 + (WIDTH - 80) * progress, 104, 108, 219, 201, filled=True)
