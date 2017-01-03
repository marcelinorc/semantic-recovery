from unittest import TestCase

from metadata.darm_instruction import DARMInstruction
from metadata.instruction import Instruction


class TestDARMInstruction(TestCase):

    def test_contruction(self):
        d = DARMInstruction("03 30 8f e0", Instruction.HEX_STR, position=9000)
        self.assertEqual(9000, d.position)
        self.assertEqual(0xe08f3003, d.encoding)
        self.assertTrue("add" in str(d.darm.instr).lower())

    def test_reglist(self):
        d = DARMInstruction("03 30 8f e0", Instruction.HEX_STR)
        self.assertTrue(15 in d.registers_used())
        self.assertTrue(3 in d.registers_used())

    def test_reg_read_write_pop_push(self):
        darm = DARMInstruction("f0 87 bd 08", Instruction.HEX_STR)
        self.assertEqual(1, len(darm.registers_read()))
        self.assertEqual(13, darm.registers_read()[0])
        self.assertEqual(8, len(darm.registers_written()))

    def test_is_branch(self):
            self.assertTrue(DARMInstruction("f7 ff ff 1a", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("66 ff ff eb", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("33 ff 2f e1", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("1e ff 2f e1", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("07 4a 08 4b", Instruction.HEX_STR).is_branch)
            self.assertTrue(DARMInstruction("3b 68 08 4a", Instruction.HEX_STR).is_branch)
