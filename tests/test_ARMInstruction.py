from unittest import TestCase

from architecture.arm_instruction import ARMInstruction, AOpType

from architecture.instruction import Instruction


class TestARMInstruction(TestCase):

    def test_conditional(self):
        # add r3, pc, r3
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
        r = arm.registers_written()
        self.assertTrue(3 in r)

    def test_registers_used_simple(self):
        # add r3, pc, r3
        arm = ARMInstruction("03 30 8f e0", Instruction.HEX_STR)
        r = arm.registers_used()
        self.assertTrue(3 in r)
        self.assertTrue(15 in r)

    def test_registers_written_ldr(self):
        # ldr	r5, [pc, #44]
        arm1 = ARMInstruction("2c 50 9f e5", Instruction.HEX_STR)
        r1 = arm1.registers_written()
        self.assertTrue(5 in r1)
        # ldr	r6, [pc, #72]
        arm2 = ARMInstruction("48 60 9f e5", Instruction.HEX_STR)
        r2 = arm2.registers_written()
        self.assertTrue(6 in r2)