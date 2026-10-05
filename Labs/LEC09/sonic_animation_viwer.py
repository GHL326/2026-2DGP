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
)
