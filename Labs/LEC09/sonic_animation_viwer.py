"""Automatic Sonic sprite viewer; run this file with Python and pico2d."""

from dataclasses import dataclass
from pathlib import Path
import sys
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
    # Travel per full animation cycle, in source-image pixels.
    stride: float = 0.0
    jump_height: float = 0.0
    braking: bool = False


def row(top, bottom, spans):
    """Explicit inclusive cell boundaries, not an assumed uniform grid."""
    return tuple((left, top, right - left + 1, bottom - top + 1)
                 for left, right in spans)


# All 76 Sonic poses in reading order. Bottom credits/mascots are not frames.
# Action names describe the visible poses; the sheet supplies no labels.
ANIMATIONS = (
    Animation("Idle", row(38, 78, ((1, 29), (31, 56), (58, 85),
                                  (86, 115), (118, 147), (150, 179), (182, 210)))),
    Animation("Look up", row(38, 78, ((211, 239), (240, 268)))),
    Animation("Crouch", row(38, 78, ((270, 293),))),
    Animation("Curl", row(38, 78, ((302, 330),))),
    Animation("Walk", row(79, 120, ((8, 33), (37, 63), (65, 95), (97, 133),
                                   (135, 166), (170, 201), (206, 231), (238, 261),
                                   (263, 292), (295, 330), (334, 365), (370, 398))), stride=24),
    Animation("Run", row(121, 164, ((1, 33), (39, 73), (89, 123),
                                   (130, 163), (181, 214), (228, 260))), stride=42),
    Animation("Roll", row(167, 200, ((1, 29), (35, 63), (67, 96), (98, 128),
                                    (131, 159), (162, 190), (193, 222), (230, 260))), stride=32),
    Animation("Ball", row(168, 200, ((268, 297),)), stride=4),
    Animation("Spin", row(205, 234, ((1, 30), (36, 64), (70, 98),
                                    (105, 133), (139, 167), (174, 202))), stride=36),
    Animation("Dash", row(237, 276, ((1, 29), (36, 65), (74, 104),
                                    (111, 141), (149, 178), (186, 216))), stride=54),
    Animation("Fast dash", row(282, 321, ((1, 29), (36, 65), (72, 110),
                                         (123, 161), (172, 210), (218, 255))), stride=72),
    Animation("Turn in air", row(326, 373, ((1, 24), (31, 59), (65, 84),
                                           (90, 114), (119, 143), (149, 168))), stride=24, jump_height=12),
    Animation("Hurt", row(327, 373, ((184, 223), (232, 270))), stride=-12, jump_height=6),
    Animation("Brake", row(377, 417, ((1, 27), (31, 61), (64, 94), (99, 131),
                                     (136, 167), (176, 208), (217, 249), (254, 286))), stride=18, braking=True),
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
    # Nearest-neighbor sampling keeps enlarged pixel art crisp.
    p.SDL_SetHint(p.SDL_HINT_RENDER_SCALE_QUALITY, b"0")
    p.open_canvas(WIDTH, HEIGHT, sync=True)
    p.hide_lattice()


def load_sprite():
    if not IMAGE_PATH.is_file():
        raise FileNotFoundError(f"Sprite image not found: {IMAGE_PATH}")
    try:
        sprite = p.load_image(str(IMAGE_PATH))
    except Exception as exc:
        raise RuntimeError(f"Cannot load sprite image: {IMAGE_PATH}") from exc
    validate_frames(sprite.w, sprite.h)
    return sprite


def frame_layout(rect, position=None):
    """Keep each row's original vertical offsets at a shared baseline."""
    _, _, w, h = rect
    x, lift = position if position is not None else (WIDTH / 2, 0.0)
    return x, BASELINE + lift + h * SCALE / 2, w * SCALE, h * SCALE


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

    @property
    def displacement(self):
        """Unwrapped travel and hop height; waiting freezes the final position."""
        animation = self.animation
        if self.state == "WAITING":
            return animation.stride * SCALE * REPEATS, 0.0
        phase = (self.frame_index + self.elapsed * FPS) / len(animation.frames)
        progress = 2 * phase - phase * phase if animation.braking else phase
        distance = animation.stride * SCALE * (self.completed + progress)
        lift = 4 * animation.jump_height * SCALE * phase * (1 - phase)
        return distance, lift

    @property
    def position(self):
        distance, lift = self.displacement
        if not self.animation.stride:
            return WIDTH / 2, lift
        # Wrap only after the entire largest frame has left the canvas.
        margin = max(f[2] for f in self.animation.frames) * SCALE / 2 + 20
        start = margin if self.animation.stride > 0 else WIDTH - margin
        x = (start + distance + margin) % (WIDTH + 2 * margin) - margin
        return x, lift

    def update(self, dt):
        self.elapsed += max(0.0, dt)
        while True:
            interval = WAIT_SECONDS if self.state == "WAITING" else 1.0 / FPS
            if self.elapsed + 1e-10 < interval:
                break
            self.elapsed = max(0.0, self.elapsed - interval)
            if self.state == "WAITING":
                self.action_index = (self.action_index + 1) % len(ANIMATIONS)
                self.frame_index = 0
                self.completed = 0
                self.state = "PLAYING"
                continue
            if self.frame_index + 1 < len(self.animation.frames):
                self.frame_index += 1
            else:
                self.completed += 1
                if self.completed == REPEATS:
                    self.state = "WAITING"
                else:
                    self.frame_index = 0


def draw_frame(sprite, rect, position=None):
    p.clear_canvas()
    sprite.clip_draw(*clip_rectangle(rect, sprite.h),
                     *frame_layout(rect, position))
    p.update_canvas()


def handle_events():
    for event in p.get_events():
        if event.type == p.SDL_QUIT:
            return False
        if event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE:
            return False
    return True


def main():
    open_window()
    sprite = None
    try:
        sprite = load_sprite()
        player = Player()
        previous = perf_counter()
        while handle_events():
            now = perf_counter()
            player.update(now - previous)
            previous = now
            draw_frame(sprite, player.frame, player.position)
            p.delay(0.001)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Sonic viewer: {exc}", file=sys.stderr)
        return 1
    finally:
        del sprite
        p.close_canvas()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
