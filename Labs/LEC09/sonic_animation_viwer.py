"""Automatic Sonic sprite viewer; run this file with Python and pico2d."""

from dataclasses import dataclass
from pathlib import Path

WIDTH, HEIGHT = 1200, 800
FPS = 10
SCALE = 10
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
