from unittest import TestCase

from metadata.instruction import Instruction
from metadata.arm_instruction import ARMInstruction, AOpType


class TestARMInstruction(TestCase):

    def test_conditional(self):
        arm = ARMInstruction("03 30 8f e0", Instruction.HEX_STR)
        self.assertEqual(arm.conditional_field(), AOpType.ALWAYS)

    def test_registers_read_simple(self):
        # add r3, pc, r3
        arm = ARMInstruction("03 30 8f e0", Instruction.HEX_STR)
        r = arm.registers_read()
        self.assertTrue(3 in r)
        self.assertTrue(15 in r)

    def test_registers_written_simple(self):
        # add r3, pc, r3
        arm = ARMInstruction("03 30 8f e0", Instruction.HEX_STR)
        r = arm.registers_read()
        self.assertTrue(3 in r)

    def test_registers_used_simple(self):
        # add r3, pc, r3
        arm = ARMInstruction("03 30 8f e0", Instruction.HEX_STR)
        r = arm.registers_used()
        self.assertTrue(3 in r)
        self.assertTrue(15 in r)
