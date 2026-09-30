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


def trim_frames(sources):
    frames = []
    for source in sources:
        bounds = source.get_bounding_rect()
        if bounds.width == 0 or bounds.height == 0:
            raise ValueError('Empty frame in the knight source archive')
        # Match the viewer's centered silhouette and common ground baseline.
        pivot = [bounds.width / 2, bounds.height]
        frames.append((source.subsurface(bounds).copy(), pivot))
    if not frames:
        raise ValueError('Animation has no source frames')
    return frames


def main():
    sources = load_source()
    packed = []
    animations = []
    atlas_width = 4096
    x = y = shelf_height = 0
    for name, key, fps in ANIMATIONS:
        frames = []
        for sprite, pivot in trim_frames(sources[key]):
            w, h = sprite.get_size()
            if x + w > atlas_width:
                x, y, shelf_height = 0, y + shelf_height + 2, 0
            packed.append((sprite, (x, y)))
            frames.append({'rect': [x, y, w, h], 'pivot': pivot})
            x += w + 2
            shelf_height = max(shelf_height, h)
        animations.append({'name': name, 'fps': fps, 'frames': frames})
    atlas = pygame.Surface((atlas_width, y + shelf_height), pygame.SRCALPHA)
    for sprite, position in packed:
        atlas.blit(sprite, position)
    pygame.image.save(atlas, str(ROOT / 'knight_atlas.png'))
    data = {'image': 'knight_atlas.png', 'animations': animations}
    (ROOT / 'animations.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
