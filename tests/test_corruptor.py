import os
from unittest import TestCase

from semantic_codec.architecture.arm_instruction import AOpType
from semantic_codec.architecture.bits import Bits
from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.corruption.corruption import corrupt_instruction, corrupt_bits, corrupt_conditional, corrupt_program, \
    corrupt_all_bits, corrupt_all_bits_tuples, predict_corruption
from semantic_codec.corruption.corruptors import PacketCorruptor, DARMInstruction, Instruction
from semantic_codec.interleaver.interleaver2d import build_2d_interleave_sp
from semantic_codec.metadata.probabilistic_rules.rules import from_instruction_list_to_dict


class TestCorruptor(TestCase):

    ASM_PATH = os.path.join(os.path.dirname(__file__), 'data/dissasembly.armasm')

    def test_corrupt_instruction(self):
        program = from_instruction_list_to_dict(TextDisassembleReader(TestCorruptor.ASM_PATH).read_instructions())
        instructions = corrupt_instruction(program, program[0x000107ac][0], 0x000107ac,
                                           conditional=True, opcode=True, registers=True, amount=3)
        for inst in instructions:
            print(inst)
        self.assertTrue(len(instructions) <= 8)
        self.assertTrue(len(instructions) > 1)


    def test_corrupt_program(self):
        program = from_instruction_list_to_dict(TextDisassembleReader(TestCorruptor.ASM_PATH).read_instructions())
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

    def test_corrupt_all_tuples_long(self):
        results = corrupt_all_bits_tuples([(0, 7), (8, 11), (15, 25)], 176)
        self.assertEqual(2**20, len(results))

    def test_predict_errors_multiword(self):
        data_len = len([3, 4, 8, 3, 5, 1, 1, 4, 9, 0, 4, 6, 2, 0, 1, 4])
        expected_errors = [(0, 30, 1), (1, 0, 1), (1, 30, 1), (2, 0, 1), (2, 30, 1), (3, 0, 1), (3, 30, 1), (4, 0, 1)]
        errors = predict_corruption(16, 2, data_len, build_2d_interleave_sp(16, flat=True), [5])
        for e in expected_errors:
            self.assertTrue(e in errors)


    def test_predict_errors(self):
        data_len = len([3, 4, 8, 3, 5, 1, 1, 4, 9, 0, 4, 6, 2, 0, 1, 4])
        errors = predict_corruption(16, 2, data_len, build_2d_interleave_sp(16, flat=True), [2, 3, 4])
        expected_errors = [(0, 4), (0, 10), (0, 16), (10, 4), (10, 10), (10, 16), (14, 16), (15, 4), (15, 10)]
        for e in expected_errors:
            self.assertTrue(e in errors)

    def test_packet_corrupt(self):
        """
        Test the Packet Corruptor
        :return:
        """
        program = {0x1000: [DARMInstruction("06 00 54 e1", Instruction.HEX_STR)],
                   0x1004: [DARMInstruction("f7 ff ff 1a", Instruction.HEX_STR)],
                   0x1008: [DARMInstruction("0c 00 9f e5", Instruction.HEX_STR)],
                   0x1028: [DARMInstruction("46 61 b0 e1", Instruction.HEX_STR)]}

        # We use a known configuration from previous test that allows to know where errors will occur
        p = PacketCorruptor(16, len(program), build_2d_interleave_sp(16, flat=True), [2, 3, 4])

        # Corrupt the program
        program = p.corrupt(program)

        # According to the parameters, instructions 0 and 10 will be corrupted, which are in memory addresses
        # 0x1000 and 0x1028 respectively. There will be three errors per instruction, therefore,
        # there will be 8 potential candidates
        self.assertEqual(64, len(program[0x1000]))
        self.assertEqual(64, len(program[0x1004]))

        # TODO: check that the instructions were in fact properly corrupted
