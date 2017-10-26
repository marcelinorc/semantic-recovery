from unittest import TestCase

from semantic_codec.architecture.arm_constants import AReg
from semantic_codec.architecture.capstone_instruction import CAPSInstruction
from semantic_codec.architecture.darm_instruction import DARMInstruction
from semantic_codec.architecture.instruction import Instruction

# The usage of Instruction.reverse_endianess in the tests is because in our old dataset
# The numbers were written from least significative from more significative
re = Instruction.reverse_endianess

class TestDARMInstruction(TestCase):

    def test_contruction(self):
        d = DARMInstruction("e0 8F 30 03", 9000, Instruction.HEX_STR)
        self.assertEqual(9000, d.address)
        self.assertEqual(0xE08F3003, d.encoding)
        self.assertTrue("add" in str(d).lower())

    def test_branch_writes_to_pc(self):
        # bl	0x00010544 <_init>
        self.assertTrue(AReg.PC in DARMInstruction(re("eb ff ff 66"), 0, Instruction.HEX_STR).storages_written())
        # blx	r3
        self.assertTrue(AReg.PC in DARMInstruction(re("33 ff 2f e1"), 0, Instruction.HEX_STR).storages_written())

    def test_modifies_flags(self):
        # cmp	r4, r6
        self.assertTrue(DARMInstruction(re("06 00 54 e1"), 0, Instruction.HEX_STR).modifies_flags())
        # asrs	r6, r6, #2
        self.assertTrue(DARMInstruction(re("46 61 b0 e1"), 0, Instruction.HEX_STR).modifies_flags())
        # bne #+-36
        self.assertFalse(DARMInstruction(re("f7 ff ff 1a"), 0, Instruction.HEX_STR).modifies_flags())
        # ldr r0, [pc, #12]
        self.assertFalse(DARMInstruction(re("0c 00 9f e5"), 0, Instruction.HEX_STR).modifies_flags())

    def test_pld(self):
        inst = DARMInstruction(4160692225, 0)
        self.assertEqual(15, inst.conditional_field)
        inst = DARMInstruction(3892256769, 0)
        self.assertEqual(14, inst.conditional_field)


    def test_reglist(self):
        d = DARMInstruction(re("03 30 8f e0"), 0, Instruction.HEX_STR)
        self.assertTrue(AReg.R15 in d.registers_used())
        self.assertTrue(AReg.R3 in d.registers_used())

    def test_reg_read_write_pop_push(self):
        darm = DARMInstruction(re("f0 87 bd 08"), 0, Instruction.HEX_STR)
        self.assertEqual(2, len(darm.registers_read()))
        self.assertTrue(AReg.R13 in darm.registers_read())
        self.assertTrue(AReg.CPSR in darm.registers_read())
        self.assertEqual(8, len(darm.registers_written()))

    def test_registers_written_ldr(self):
        # ldr	r5, [pc, #44]
        arm1 = DARMInstruction(re("2c 50 9f e5"), 0, Instruction.HEX_STR)
        r1 = arm1.registers_written()
        self.assertTrue(AReg.R5 in r1)
        # ldr	r6, [pc, #72]
        arm2 = DARMInstruction(re("48 60 9f e5"), 0, Instruction.HEX_STR)
        r2 = arm2.registers_written()
        self.assertTrue(AReg.R6 in r2)

    def test_read_from_memory(self):
        # ldr	r6, [pc, #72]	; 0x000107f0 <$d>
        self.assertTrue(AReg.STORE in DARMInstruction(re("48 60 9f e5"), 0, Instruction.HEX_STR).storages_read())
        # popeq	{r4, r5, r6, r7, r8, r9, sl, pc}
        self.assertTrue(AReg.STORE in DARMInstruction(re("f0 87 bd 08"), 0, Instruction.HEX_STR).storages_read())
        # ldr	r3, [r5], #4
        self.assertTrue(AReg.STORE in DARMInstruction(re("04 30 95 e4"), 0, Instruction.HEX_STR).storages_read())
        # pop	{r4, r5, r6, r7, r8, r9, sl, pc}
        self.assertTrue(AReg.STORE in DARMInstruction(re("f0 87 bd e8"), 0, Instruction.HEX_STR).storages_read())

        # push	{r4, r5, r6, r7, r8, r9, sl, lr}
        self.assertFalse(AReg.STORE in DARMInstruction(re("f0 47 2d e9"), 0, Instruction.HEX_STR).storages_read())
        # mov	r1, r8
        self.assertFalse(AReg.STORE in DARMInstruction(re("08 10 a0 e1"), 0, Instruction.HEX_STR).storages_read())

    def test_writes_to_memory(self):
        # push	{r4, r5, r6, r7, r8, r9, sl, lr}
        self.assertTrue(AReg.STORE in DARMInstruction(re("f0 47 2d e9"), 0, Instruction.HEX_STR).storages_written())

    def test_is_branch(self):
        self.assertTrue(DARMInstruction(re("f7 ff ff 1a"), 0, Instruction.HEX_STR).is_branch)
        self.assertTrue(DARMInstruction(re("66 ff ff eb"), 0, Instruction.HEX_STR).is_branch)
        self.assertTrue(DARMInstruction(re("33 ff 2f e1"), 0, Instruction.HEX_STR).is_branch)
        self.assertTrue(DARMInstruction(re("1e ff 2f e1"), 0, Instruction.HEX_STR).is_branch)
        self.assertTrue(DARMInstruction(re("07 4a 08 4b"), 0, Instruction.HEX_STR).is_branch)
        self.assertTrue(DARMInstruction(re("3b 68 08 4a"), 0, Instruction.HEX_STR).is_branch)
