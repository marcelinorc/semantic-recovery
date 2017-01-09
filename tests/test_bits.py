from unittest import TestCase

from architecture.bits import Bits


class TestBits(TestCase):
    def test_is_on(self):
        self.assertTrue(Bits.is_on(0xE0000000, 31))

    def test_are_on(self):
        self.assertTrue(Bits.are_on(0xE0000000, 31, 29))
        self.assertTrue(Bits.are_on(0xE0000000, 30, 29))
        self.assertTrue(Bits.are_on(0x000000FF, 6, 4))
        self.assertTrue(Bits.are_on(0x000000FF, 8, 0))

    def test_set(self):
        self.assertEqual(0xE0000000, Bits.set(31, 29))

    def test_on(self):
        self.assertEqual(2**31, Bits.on(31))
        self.assertTrue(1, Bits.on(0))
