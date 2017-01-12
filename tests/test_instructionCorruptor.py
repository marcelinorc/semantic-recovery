from unittest import TestCase

from semantic_codec.architecture.arm_instruction import AOpType
from semantic_codec.architecture.bits import Bits
from tests.corruptor import corrupt_bits, corrupt_conditional


class TestInstructionCorruptor(TestCase):

    def test_corrupt_bits(self):
        # ldr	r5, [pc, #44]
        corrupted = corrupt_bits(31, 28, 2, 0xe59f502c)
        self.assertEqual(4, len(corrupted))
        mask = Bits.set(31, 28)
        self.assertTrue(corrupted[0] & mask == AOpType.ALWAYS)
        self.assertFalse(corrupted[1] & mask == AOpType.ALWAYS)
        self.assertFalse(corrupted[2] & mask == AOpType.ALWAYS)
        self.assertFalse(corrupted[3] & mask == AOpType.ALWAYS)

    def test_corrupt_conditional(self):
        # ldr	r5, [pc, #44]
        corrupted = corrupt_conditional(2, 0xe59f502c)
        self.assertEqual(4, len(corrupted))
        mask = Bits.set(31, 28)
        self.assertTrue((corrupted[0] & mask) == AOpType.ALWAYS)
        self.assertFalse((corrupted[1] & mask) == AOpType.ALWAYS, "{:b} - {:b}".format(corrupted[1], AOpType.ALWAYS))
        self.assertFalse((corrupted[2] & mask) == AOpType.ALWAYS, "{:b} - {:b}".format(corrupted[2], AOpType.ALWAYS))
        self.assertFalse((corrupted[3] & mask) == AOpType.ALWAYS, "{:b} - {:b}".format(corrupted[3], AOpType.ALWAYS))