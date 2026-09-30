import unittest

from animation_viewer import (
    Player, REPEATS, PAUSE_SECONDS, SCALE, WIDTH, HEIGHT, BASELINE,
    frame_destination, load_animations, validate_animations,
)


class PlaybackTests(unittest.TestCase):
    def setUp(self):
        _, self.animations = load_animations()
        self.player = Player(self.animations)

    def test_every_frame_for_exactly_five_repeats(self):
        for index, animation in enumerate(self.animations):
            self.player.index = index
            for tick in range(len(animation.frames) * REPEATS):
                self.player.elapsed = 0
                self.player.advance((tick + 0.5) / animation.fps)
                self.assertFalse(self.player.holding)
                self.assertEqual(self.player.frame_index, tick % len(animation.frames))
                self.assertEqual(self.player.repeat_number, tick // len(animation.frames) + 1)

    def test_hold_and_transition_for_every_animation(self):
        for index, animation in enumerate(self.animations):
            player = Player(self.animations)
            player.index = index
            player.advance(player.play_seconds)
            self.assertTrue(player.holding)
            self.assertEqual(player.frame_index, len(animation.frames) - 1)
            player.advance(PAUSE_SECONDS - 0.001)
            self.assertEqual(player.index, index)
            player.advance(0.002)
            self.assertEqual(player.index, (index + 1) % len(self.animations))
            self.assertAlmostEqual(player.elapsed, 0.001)

    def test_long_delay_preserves_cycle_and_remainder(self):
        cycle = sum(len(a.frames) * REPEATS / a.fps + PAUSE_SECONDS for a in self.animations)
        self.player.advance(cycle * 100 + 0.25)
        self.assertEqual(self.player.index, 0)
        self.assertAlmostEqual(self.player.elapsed, 0.25)

    def test_invalid_delta_rejected(self):
        for delta in (-1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                self.player.advance(delta)


class AssetTests(unittest.TestCase):
    def test_variable_frame_sizes_and_counts(self):
        image_path, animations = load_animations()
        self.assertTrue(image_path.is_file())
        self.assertEqual(image_path.name, 'knight_atlas.png')
        self.assertEqual([a.name for a in animations], ['Idle', 'Walk', 'Run', 'Sword Attack', 'Spin Attack'])
        self.assertEqual([len(a.frames) for a in animations], [40, 20, 20, 14, 16])
        self.assertGreater(len({f.rect[2:] for a in animations for f in a.frames}), 1)
        # Read dimensions from the standard PNG IHDR header, without pygame.
        import struct
        width, height = struct.unpack('>II', image_path.read_bytes()[16:24])
        validate_animations(animations, width, height)

    def test_every_sprite_is_large_and_inside_stage(self):
        _, animations = load_animations()
        for animation in animations:
            for frame in animation.frames:
                x, y, w, h = frame_destination(frame)
                self.assertGreaterEqual(h, HEIGHT / 2)
                self.assertGreaterEqual(x - w / 2, 28)
                self.assertLessEqual(x + w / 2, WIDTH - 28)
                self.assertGreaterEqual(y - h / 2, 110 - 1e-9)
                self.assertLessEqual(y + h / 2, 600)
                self.assertAlmostEqual(x - w / 2 + frame.pivot[0] * SCALE, WIDTH / 2)
                self.assertAlmostEqual(y + h / 2 - frame.pivot[1] * SCALE, BASELINE)


if __name__ == '__main__':
    unittest.main()
