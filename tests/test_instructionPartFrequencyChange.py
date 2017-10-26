import os
from unittest import TestCase

from semantic_codec.architecture.capstone_instruction import CAPSInstruction
from semantic_codec.architecture.disassembler_readers import ElfioTextDisassembleReader
from semantic_codec.compressor.huffman import InstructionPartFrequencyChanger, InstructionPartFrequencyCounter
from semantic_codec.distributed.qos_functions import MockQoSFunction


class TestInstructionPartFrequencyChange(TestCase):

    def create_program(self):
        program = []
        program.append(CAPSInstruction('e1a03000', 0))  # mov;r3, r0
        program.append(CAPSInstruction('e59f1018', 1))  # ldr;r1, [pc, #0x18]
        program.append(CAPSInstruction('e1a00003', 2))  # mov;r0, r3
        program.append(CAPSInstruction('ebffff9e', 3))  # bl;#0x10594
        program.append(CAPSInstruction('e3a03000', 4))  # mov;r3, #0
        program.append(CAPSInstruction('e1a00003', 5))  # mov;r0, r3
        program.append(CAPSInstruction('e8bd8800', 6))  # pop;{fp, pc}
        program.append(CAPSInstruction('00010830', 7))  # andeq;r0, r1, r0, lsr r8
        program.append(CAPSInstruction('000209b4', 8))  # strheq;r0, [r2], -r4
        program.append(CAPSInstruction('00010570', 9))  # andeq;r0, r1, r0, ror r5
        return program

    def test_change_registers(self):
        # We got these numbers from another unit test
        program = self.create_program()
        # Got this numbers from the frequency counter
        fc = InstructionPartFrequencyCounter()
        fc.count(program)

        qos = MockQoSFunction() # Say yes every fifth change
        changer = InstructionPartFrequencyChanger(program, qos, fc)
        # Try to change the registers
        #changer.change_registers()
        self.fail()

