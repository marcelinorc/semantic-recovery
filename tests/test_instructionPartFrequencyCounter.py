import os
from unittest import TestCase

from semantic_codec.architecture.arm_constants import AReg
from semantic_codec.architecture.disassembler_readers import ElfioTextDisassembleReader
from semantic_codec.compressor.huffman import InstructionPartFrequencyCounter


class TestInstructionPartFrequencyCounter(TestCase):

    def test_count(self):
        ARM_SIMPLE = os.path.join(os.path.dirname(__file__), 'data/helloworld_elfiodissasembly.disam')
        program = ElfioTextDisassembleReader(ARM_SIMPLE).read_instructions()
        fc = InstructionPartFrequencyCounter()
        fc.count(program)
        self.assertTrue(fc.reg_frequency[AReg.R0], 33)
        self.assertTrue(fc.reg_frequency[AReg.R1], 17)
        self.assertTrue(fc.cond_frequency[14], 115)
        self.assertTrue(fc.opcode_frequency[23], 9)

        #print(fc.reg_frequency)
        #print(fc.cond_frequency)
        #print(fc.opcode_frequency)