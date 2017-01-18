import os
from unittest import TestCase

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.metadata.rules import from_instruction_list_to_dict
from tests.corruptor import corrupt_instruction


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
