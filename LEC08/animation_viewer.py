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
