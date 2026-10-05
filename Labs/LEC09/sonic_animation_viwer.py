"""Automatic Sonic sprite viewer; run this file with Python and pico2d."""

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import pico2d as p

WIDTH, HEIGHT = 1200, 800
FPS = 10
SCALE = 10
BASELINE = 160
REPEATS = 5
WAIT_SECONDS = 1.0
IMAGE_PATH = Path(__file__).resolve().with_name("sonic-sprite.png")


@dataclass(frozen=True)
class Animation:
    name: str
    # Rectangles use top-left image coordinates: x, y, width, height.
    frames: tuple[tuple[int, int, int, int], ...]


def row(top, bottom, spans):
    """Explicit inclusive cell boundaries, not an assumed uniform grid."""
    return tuple((left, top, right - left + 1, bottom - top + 1)
                 for left, right in spans)


# All 76 Sonic poses in reading order. Bottom credits/mascots are not frames.
# Action names describe the visible poses; the sheet supplies no labels.
ANIMATIONS = (
    Animation("Idle", row(38, 78, ((1, 29), (31, 56), (58, 85),
                                  (87, 115), (118, 147), (150, 179), (182, 211)))),
    Animation("Look up", row(38, 78, ((213, 240), (242, 268)))),
    Animation("Crouch", row(38, 78, ((270, 293),))),
    Animation("Curl", row(38, 78, ((302, 330),))),
    Animation("Walk", row(79, 120, ((8, 33), (37, 63), (65, 95), (97, 133),
                                   (135, 166), (170, 201), (206, 231), (238, 261),
                                   (263, 292), (295, 330), (334, 365), (370, 398)))),
    Animation("Run", row(122, 164, ((1, 33), (39, 73), (89, 123),
                                   (130, 163), (181, 214), (228, 260)))),
    Animation("Roll", row(168, 200, ((1, 29), (35, 63), (67, 96), (98, 128),
                                    (131, 159), (162, 190), (193, 222), (230, 260)))),
    Animation("Ball", row(168, 200, ((268, 297),))),
    Animation("Spin", row(205, 234, ((1, 30), (36, 64), (70, 98),
                                    (105, 133), (139, 167), (174, 202)))),
    Animation("Dash", row(237, 276, ((1, 29), (36, 65), (74, 104),
                                    (111, 141), (149, 178), (186, 216)))),
    Animation("Fast dash", row(282, 321, ((1, 29), (36, 65), (72, 110),
                                         (123, 161), (172, 210), (218, 255)))),
    Animation("Turn in air", row(327, 373, ((1, 24), (31, 59), (65, 84),
                                           (90, 114), (119, 143), (149, 168)))),
    Animation("Hurt", row(327, 373, ((184, 223), (232, 270)))),
    Animation("Brake", row(378, 417, ((1, 27), (31, 61), (64, 94), (99, 131),
                                     (136, 167), (176, 208), (217, 249), (254, 286)))),
    Animation("Surprised", row(426, 469, ((6, 39), (49, 82)))),
    Animation("Stand", row(426, 469, ((96, 118), (125, 147)))),
)


def validate_frames(image_width, image_height):
    """Reject empty, duplicate or out-of-image rectangles before rendering."""
    seen = set()
    for animation in ANIMATIONS:
        if not animation.frames:
            raise ValueError(f"No frames: {animation.name}")
        for rect in animation.frames:
            x, y, w, h = rect
            if min(x, y) < 0 or min(w, h) <= 0:
                raise ValueError(f"Invalid frame: {animation.name} {rect}")
            if x + w > image_width or y + h > image_height:
                raise ValueError(f"Frame outside image: {animation.name} {rect}")
            if rect in seen:
                raise ValueError(f"Duplicate frame: {animation.name} {rect}")
            seen.add(rect)


def clip_rectangle(rect, image_height):
    x, top, w, h = rect
    return x, image_height - top - h, w, h


def open_window():
    p.open_canvas(WIDTH, HEIGHT, sync=True)
    p.hide_lattice()


def load_sprite():
    sprite = p.load_image(str(IMAGE_PATH))
    validate_frames(sprite.w, sprite.h)
    return sprite


def frame_layout(rect):
    """Keep each row's original vertical offsets at a shared baseline."""
    _, _, w, h = rect
    return WIDTH / 2, BASELINE + h * SCALE / 2, w * SCALE, h * SCALE


@dataclass
class Player:
    action_index: int = 0
    frame_index: int = 0
    completed: int = 0
    elapsed: float = 0.0
    state: str = "PLAYING"

    @property
    def animation(self):
        return ANIMATIONS[self.action_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, dt):
        if self.state != "PLAYING":
            return
        self.elapsed += max(0.0, dt)
        interval = 1.0 / FPS
        while self.elapsed + 1e-10 >= interval:
            self.elapsed = max(0.0, self.elapsed - interval)
            if self.frame_index + 1 < len(self.animation.frames):
                self.frame_index += 1
            else:
                self.completed += 1
                if self.completed == REPEATS:
                    self.state = "WAITING"
                    self.elapsed = 0.0
                    break
                self.frame_index = 0


def draw_frame(sprite, rect):
    p.clear_canvas()
    sprite.clip_draw(*clip_rectangle(rect, sprite.h),
                     *frame_layout(rect))
    p.update_canvas()


def main():
    open_window()
    sprite = load_sprite()
    player = Player()
    previous = perf_counter()
    running = True
    while running:
        for event in p.get_events():
            if event.type == p.SDL_QUIT:
                running = False
        now = perf_counter()
        player.update(now - previous)
        previous = now
        draw_frame(sprite, player.frame)
        p.delay(0.001)
    del sprite
    p.close_canvas()


if __name__ == "__main__":
    main()
