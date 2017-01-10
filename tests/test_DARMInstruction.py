from unittest import TestCase
from semantic_codec.architecture.arm_instruction import AReg
from semantic_codec.architecture.darm_instruction import DARMInstruction
from semantic_codec.architecture.instruction import Instruction


class TestDARMInstruction(TestCase):

    def test_contruction(self):
        d = DARMInstruction("03 30 8f e0", Instruction.HEX_STR, position=9000)
        self.assertEqual(9000, d.position)
        self.assertEqual(0xe08f3003, d.encoding)
        self.assertTrue("add" in str(d.darm.instr).lower())

    def test_reglist(self):
        d = DARMInstruction("03 30 8f e0", Instruction.HEX_STR)
        self.assertTrue(AReg.R15 in d.registers_used())
        self.assertTrue(AReg.R3 in d.registers_used())

    def test_reg_read_write_pop_push(self):
        darm = DARMInstruction("f0 87 bd 08", Instruction.HEX_STR)
        self.assertEqual(2, len(darm.registers_read()))
        self.assertTrue(AReg.R13 in darm.registers_read())
        self.assertTrue(AReg.CPSR in darm.registers_read())
        self.assertEqual(8, len(darm.registers_written()))

    def test_registers_written_ldr(self):
        # ldr	r5, [pc, #44]
        arm1 = DARMInstruction("2c 50 9f e5", Instruction.HEX_STR)
        r1 = arm1.registers_written()
        self.assertTrue(AReg.R5 in r1)
        # ldr	r6, [pc, #72]
        arm2 = DARMInstruction("48 60 9f e5", Instruction.HEX_STR)
        r2 = arm2.registers_written()
        self.assertTrue(AReg.R6 in r2)

    def test_read_from_memory(self):
        # ldr	r6, [pc, #72]	; 0x000107f0 <$d>
        self.assertTrue(AReg.STORE in DARMInstruction("48 60 9f e5", Instruction.HEX_STR).storages_read())
        # popeq	{r4, r5, r6, r7, r8, r9, sl, pc}
        self.assertTrue(AReg.STORE in DARMInstruction("f0 87 bd 08", Instruction.HEX_STR).storages_read())
        # ldr	r3, [r5], #4
        self.assertTrue(AReg.STORE in DARMInstruction("04 30 95 e4", Instruction.HEX_STR).storages_read())
        # pop	{r4, r5, r6, r7, r8, r9, sl, pc}
        self.assertTrue(AReg.STORE in DARMInstruction("f0 87 bd e8", Instruction.HEX_STR).storages_read())

        # push	{r4, r5, r6, r7, r8, r9, sl, lr}
        self.assertFalse(AReg.STORE in DARMInstruction("f0 47 2d e9", Instruction.HEX_STR).storages_read())
        # mov	r1, r8
        self.assertFalse(AReg.STORE in DARMInstruction("08 10 a0 e1", Instruction.HEX_STR).storages_read())

    def test_writes_to_memory(self):
        # push	{r4, r5, r6, r7, r8, r9, sl, lr}
        self.assertTrue(AReg.STORE in DARMInstruction("f0 47 2d e9", Instruction.HEX_STR).storages_written())

    def test_is_branch(self):
            self.assertTrue(DARMInstruction("f7 ff ff 1a", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("66 ff ff eb", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("33 ff 2f e1", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("1e ff 2f e1", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("07 4a 08 4b", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("3b 68 08 4a", Instruction.HEX_STR).is_branch)
