import unittest
from fractions import Fraction

from hyperscore.core import TimeSpan
from hyperscore.rhythm import parse_rhythm, rhythm_ast_to_timespans
from hyperscore.rhythm.rhythm_tree import Atom, Group, Repeat, Sequence, Split


class TestRhythmTree(unittest.TestCase):
    def test_parse_single_atom(self):
        ast = parse_rhythm("1")
        assert isinstance(ast, Sequence)
        self.assertEqual(len(ast.items), 1)

        atom = ast.items[0]
        assert isinstance(atom, Atom)
        self.assertEqual(atom.value, Fraction(1, 1))

    def test_parse_fraction_atom(self):
        ast = parse_rhythm("1/2")
        assert isinstance(ast, Sequence)
        self.assertEqual(len(ast.items), 1)

        atom = ast.items[0]
        assert isinstance(atom, Atom)
        self.assertEqual(atom.value, Fraction(1, 2))

    def test_parse_sequence(self):
        ast = parse_rhythm("1 2 3")
        assert isinstance(ast, Sequence)
        self.assertEqual(len(ast.items), 3)

        values = [Fraction(1), Fraction(2), Fraction(3)]
        for i in range(3):
            atom = ast.items[i]
            assert isinstance(atom, Atom)
            self.assertEqual(atom.value, values[i])

    def test_parse_group(self):
        ast = parse_rhythm("1[1 2]")
        assert isinstance(ast, Sequence)
        self.assertEqual(len(ast.items), 1)

        node = ast.items[0]
        assert isinstance(node, Group)
        self.assertEqual(node.weight.value, Fraction(1))

        assert isinstance(node.body, Sequence)

        values = [Fraction(1), Fraction(2)]
        for i in range(2):
            atom = node.body.items[i]
            assert isinstance(atom, Atom)
            self.assertEqual(atom.value, values[i])

    def test_parse_split(self):
        ast = parse_rhythm("1%3")
        assert isinstance(ast, Sequence)

        node = ast.items[0]
        assert isinstance(node, Split)

        self.assertEqual(node.parts, 3)
        assert isinstance(node.node, Atom)

    def test_parse_repeat(self):
        ast = parse_rhythm("(1 2)*3")
        assert isinstance(ast, Sequence)

        node = ast.items[0]
        assert isinstance(node, Repeat)

        self.assertEqual(node.times, 3)

    def test_parse_postfix_order(self):
        ast = parse_rhythm("1%3*2")
        assert isinstance(ast, Sequence)

        node = ast.items[0]
        assert isinstance(node, Repeat)
        assert isinstance(node.node, Split)

    def test_ticks_single_atom(self):
        ast = parse_rhythm("1")
        spans = rhythm_ast_to_timespans(ast, total=1000)
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0], TimeSpan(0, 1000))

    def test_ticks_simple_sequence(self):
        ast = parse_rhythm("1 1")
        spans = rhythm_ast_to_timespans(ast, total=1000)
        self.assertEqual(len(spans), 2)
        self.assertEqual(spans[0], TimeSpan(0, 500))
        self.assertEqual(spans[1], TimeSpan(500, 500))

    def test_ticks_fraction_weight(self):
        ast = parse_rhythm("1/2 1/2")
        spans = rhythm_ast_to_timespans(ast, total=1000)
        self.assertEqual(len(spans), 2)
        self.assertEqual(spans[0], TimeSpan(0, 500))
        self.assertEqual(spans[1], TimeSpan(500, 500))

    def test_ticks_group(self):
        ast = parse_rhythm("1/2[1 2] 1")
        spans = rhythm_ast_to_timespans(ast, total=1000)
        self.assertEqual(len(spans), 3)
        self.assertEqual(spans[0], TimeSpan(0, 111))
        self.assertEqual(spans[1], TimeSpan(111, 222))
        self.assertEqual(spans[2], TimeSpan(333, 667))

    def test_ticks_split(self):
        ast = parse_rhythm("1%4")
        spans = rhythm_ast_to_timespans(ast, total=1000)
        self.assertEqual(len(spans), 4)
        self.assertEqual(spans[0], TimeSpan(0, 250))
        self.assertEqual(spans[1], TimeSpan(250, 250))
        self.assertEqual(spans[2], TimeSpan(500, 250))
        self.assertEqual(spans[3], TimeSpan(750, 250))

    def test_ticks_repeat(self):
        ast = parse_rhythm("1*3")
        spans = rhythm_ast_to_timespans(ast, total=900)
        self.assertEqual(len(spans), 3)
        self.assertEqual(spans[0], TimeSpan(0, 300))
        self.assertEqual(spans[1], TimeSpan(300, 300))
        self.assertEqual(spans[2], TimeSpan(600, 300))

    def test_ticks_repeat_sequence(self):
        ast = parse_rhythm("(1 2)*3")
        spans = rhythm_ast_to_timespans(ast, total=900)
        self.assertEqual(len(spans), 6)
        self.assertEqual(spans[0], TimeSpan(0, 100))
        self.assertEqual(spans[1], TimeSpan(100, 200))
        self.assertEqual(spans[2], TimeSpan(300, 100))
        self.assertEqual(spans[3], TimeSpan(400, 200))
        self.assertEqual(spans[4], TimeSpan(600, 100))
        self.assertEqual(spans[5], TimeSpan(700, 200))

    def test_ticks_split_repeat_combo(self):
        ast = parse_rhythm("1%3*2")
        spans = rhythm_ast_to_timespans(ast, total=1200)
        self.assertEqual(len(spans), 6)
        self.assertEqual(spans[0], TimeSpan(0, 200))
        self.assertEqual(spans[1], TimeSpan(200, 200))
        self.assertEqual(spans[2], TimeSpan(400, 200))
        self.assertEqual(spans[3], TimeSpan(600, 200))
        self.assertEqual(spans[4], TimeSpan(800, 200))
        self.assertEqual(spans[5], TimeSpan(1000, 200))

    def test_ticks_largest_remainder(self):
        ast = parse_rhythm("1 2")
        spans = rhythm_ast_to_timespans(ast, total=1000)
        self.assertEqual(len(spans), 2)
        self.assertEqual(spans[0], TimeSpan(0, 333))
        self.assertEqual(spans[1], TimeSpan(333, 667))

    def test_ticks_nested_complex(self):
        ast = parse_rhythm("1/2[(1%3) 2] 3")
        spans = rhythm_ast_to_timespans(ast, total=1200)
        self.assertEqual(len(spans), 5)
        self.assertEqual(sum([s.duration for s in spans]), 1200)

    def test_invalid_total_ticks(self):
        ast = parse_rhythm("1 1")
        with self.assertRaises(ValueError):
            rhythm_ast_to_timespans(ast, total=0)
