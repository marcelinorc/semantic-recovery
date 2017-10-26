from unittest import TestCase

from semantic_codec.architecture.capstone_instruction import CAPSInstruction
from semantic_codec.architecture.instruction_modifier import InstructionModifier


class TestInstructionModifier(TestCase):
    def test_modify_cond(self):
        self.fail()

    def test_modify_opcode(self):
        self.fail()

    def test_modify_rn(self):
        inst = CAPSInstruction('000209b4', 8)  # strheq;r0, [r2], -r4
        mod = InstructionModifier()
        self.assertEqual('strheq\tr0, [r0], -r4', str(CAPSInstruction(mod.modify_rn(inst.encoding, 0), 8)))
        self.assertEqual('strheq\tr0, [r4], -r4', str(CAPSInstruction(mod.modify_rn(inst.encoding, 4), 8)))
        self.assertEqual('strheq\tr0, [sl], -r4', str(CAPSInstruction(mod.modify_rn(inst.encoding, 10), 8)))

    def test_modify_rd(self):
        self.fail()

    def test_modify_rs(self):
        self.fail()

    def test_modify_rm(self):
        self.fail()

    def test_modify_immediate(self):
        self.fail()

    def test_modify_register(self):
        self.fail()

    def test_modify_register_list(self):
        self.fail()
