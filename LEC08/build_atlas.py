"""Build a variable-size knight sprite sheet from the bundled CC0 PNG frames."""
import json
import os
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

ROOT = Path(__file__).resolve().parent
ANIMATIONS = (
    ('Idle', 'Idle', 20),
    ('Walk', 'Walk', 16),
    ('Run', 'Run', 24),
    ('Sword Attack', 'Attack', 18),
    ('Spin Attack', 'Attack2', 18),
)


def load_source():
    with ZipFile(ROOT / 'knight_source.zip') as archive:
        return {
            key: [pygame.image.load(BytesIO(archive.read(name)))
                  for name in sorted(archive.namelist())
                  if name.startswith(f'Knight-{key}_') and name.endswith('.png')]
            for _, key, _ in ANIMATIONS
        }

