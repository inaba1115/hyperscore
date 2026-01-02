import unittest
from fractions import Fraction

from hyperscore.rhythm_tree import Atom, Group, Repeat, Sequence, Split, parse_rhythm, rhythm_ast_to_ticks


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
        ticks = rhythm_ast_to_ticks(ast, total_ticks=1000)
        self.assertEqual(ticks, [1000])

    def test_ticks_simple_sequence(self):
        ast = parse_rhythm("1 1")
        ticks = rhythm_ast_to_ticks(ast, total_ticks=1000)
        self.assertEqual(ticks, [500, 500])

    def test_ticks_fraction_weight(self):
        ast = parse_rhythm("1/2 1/2")
        ticks = rhythm_ast_to_ticks(ast, total_ticks=1000)
        self.assertEqual(ticks, [500, 500])

    def test_ticks_group(self):
        ast = parse_rhythm("1/2[1 2] 1")
        ticks = rhythm_ast_to_ticks(ast, total_ticks=1000)
        self.assertEqual(ticks, [111, 222, 667])
        self.assertEqual(sum(ticks), 1000)

    def test_ticks_split(self):
        ast = parse_rhythm("1%4")
        ticks = rhythm_ast_to_ticks(ast, total_ticks=1000)
        self.assertEqual(ticks, [250, 250, 250, 250])

    def test_ticks_repeat(self):
        ast = parse_rhythm("1*3")
        ticks = rhythm_ast_to_ticks(ast, total_ticks=900)
        self.assertEqual(ticks, [300, 300, 300])

    def test_ticks_repeat_sequence(self):
        ast = parse_rhythm("(1 2)*3")
        ticks = rhythm_ast_to_ticks(ast, total_ticks=900)
        self.assertEqual(ticks, [100, 200, 100, 200, 100, 200])

    def test_ticks_split_repeat_combo(self):
        ast = parse_rhythm("1%3*2")
        ticks = rhythm_ast_to_ticks(ast, total_ticks=1200)
        self.assertEqual(ticks, [200] * 6)
        self.assertEqual(sum(ticks), 1200)

    def test_ticks_largest_remainder(self):
        ast = parse_rhythm("1 2")
        ticks = rhythm_ast_to_ticks(ast, total_ticks=1000)
        self.assertEqual(ticks, [333, 667])
        self.assertEqual(sum(ticks), 1000)

    def test_ticks_nested_complex(self):
        ast = parse_rhythm("1/2[(1%3) 2] 3")
        ticks = rhythm_ast_to_ticks(ast, total_ticks=1200)
        self.assertEqual(sum(ticks), 1200)
        self.assertEqual(len(ticks), 5)

    def test_invalid_total_ticks(self):
        ast = parse_rhythm("1 1")
        with self.assertRaises(ValueError):
            rhythm_ast_to_ticks(ast, total_ticks=0)
