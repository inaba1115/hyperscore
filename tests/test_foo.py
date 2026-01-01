import unittest

import hyperscore


class TestFoo(unittest.TestCase):
    def test_add(self):
        self.assertEqual(hyperscore.add(1, 2), 3)
