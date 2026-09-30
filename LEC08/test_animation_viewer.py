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


if __name__ == '__main__':
    unittest.main()
