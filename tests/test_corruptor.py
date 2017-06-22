import os
from unittest import TestCase

from semantic_codec.architecture.arm_instruction import AOpType
from semantic_codec.architecture.bits import Bits
from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.corruption.corruptor import corrupt_instruction, corrupt_bits, corrupt_conditional, corrupt_program, \
    corrupt_all_bits, corrupt_all_bits_tuples
from semantic_codec.metadata.rules import from_instruction_list_to_dict


class TestCorruptor(TestCase):

    ASM_PATH = os.path.join(os.path.dirname(__file__), 'data/dissasembly.armasm')

    def test_corrupt_instruction(self):
        program = from_instruction_list_to_dict(TextDisassembleReader(TestCorruptor.ASM_PATH).read())
        instructions = corrupt_instruction(program, program[0x000107ac][0], 0x000107ac,
                                           conditional=True, opcode=True, registers=True, amount=3)
        for inst in instructions:
            print(inst)
        self.assertTrue(len(instructions) <= 8)
        self.assertTrue(len(instructions) > 1)


    def test_corrupt_program(self):
        program = from_instruction_list_to_dict(TextDisassembleReader(TestCorruptor.ASM_PATH).read())
        corrupt_program(program, 10.0, 2)
        corrupted = 0
        for v in program.values():
            #s = " -- "
            #for i in v:
            #    s += str(i) + " -- "
            #print(s)
            if len(v) > 0:
                corrupted += 1
        self.assertTrue(corrupted >= 2)

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

    def test_corrupt_all_bits(self):
        results3 = corrupt_all_bits(0, 3, 3)
        results0 = corrupt_all_bits(0, 3, 0)
        self.assertEqual(8, len(results0))
        self.assertEqual(8, len(results3))
        for x in range(0, 7):
            self.assertTrue(x in results3)
            self.assertTrue(x in results0)

    def test_corrupt_all_tuples(self):
        results = corrupt_all_bits_tuples([(0, 3), (8, 11)], 176)
        self.assertEqual(64, len(results))
        for i in range(0, 3):
            for j in range(0, 3):
                x = (j << 8) + i + 176
                self.assertTrue(x in results)