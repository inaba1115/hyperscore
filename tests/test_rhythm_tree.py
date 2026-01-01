import unittest

import hyperscore


class TestRhythmTree(unittest.TestCase):
    def test_parse_rhythm(self):
        ast = hyperscore.parse_rhythm("1 2")
        ticks = hyperscore.rhythm_to_ticks(ast, total_ticks=300)
        self.assertEqual(ticks, [100, 200])

        ast = hyperscore.parse_rhythm("1*3")
        ticks = hyperscore.rhythm_to_ticks(ast, total_ticks=1000)
        self.assertEqual(ticks, [334, 333, 333])

        ast = hyperscore.parse_rhythm("(1)*3")
        ticks = hyperscore.rhythm_to_ticks(ast, total_ticks=1000)
        self.assertEqual(ticks, [334, 333, 333])

        ast = hyperscore.parse_rhythm("1/3")
        ticks = hyperscore.rhythm_to_ticks(ast, total_ticks=1000)
        self.assertEqual(ticks, [334, 333, 333])

        ast = hyperscore.parse_rhythm("(1/2)*2")
        ticks = hyperscore.rhythm_to_ticks(ast, total_ticks=400)
        self.assertEqual(ticks, [100, 100, 100, 100])

        ast = hyperscore.parse_rhythm("1 3[1 2]")
        ticks = hyperscore.rhythm_to_ticks(ast, total_ticks=400)
        self.assertEqual(ticks, [100, 100, 200])

        ast = hyperscore.parse_rhythm("1 3[1/2 2[1 2[1 1] 1]]")
        ticks = hyperscore.rhythm_to_ticks(ast, total_ticks=400)
        self.assertEqual(ticks, [100, 50, 50, 50, 50, 50, 50])
