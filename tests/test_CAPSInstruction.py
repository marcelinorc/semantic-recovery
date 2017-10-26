from unittest import TestCase
from capstone.arm_const import *
from semantic_codec.architecture.arm_constants import AReg
from semantic_codec.architecture.capstone_instruction import CAPSInstruction

class TestCAPSInstruction(TestCase):

    def test_encoding(self):
        from_str = CAPSInstruction('000209b4', 8)
        from_int = CAPSInstruction(0x000209b4, 8)
        self.assertEqual(str(from_str), 'strheq\tr0, [r2], -r4')
        self.assertEqual(str(from_int), 'strheq\tr0, [r2], -r4')


    def test_constructor(self):
        caps = CAPSInstruction(0xe52de004, 0x10550)
        self.assertEqual(0x10550, caps.address)
        self.assertEqual(str(caps), 'str\tlr, [sp, #-4]!')
        # This is optional, but I need to check
        self.assertEqual(0x10550, caps._cap.address)

    def test_conditional_field(self):
        caps = CAPSInstruction(0xe52de004, 0x10550)  # str;lr, [sp, #-4]!
        self.assertEqual(caps.conditional_field, ARM_CC_AL - 1)

        caps = CAPSInstruction(0x106f4, 0x10550) # strdeq r0, r1, [r1], -r4
        self.assertEqual(caps.conditional_field, ARM_CC_EQ - 1)

        caps = CAPSInstruction(0x18bd8010, 0x10550) # popne;{r4, pc}
        self.assertEqual(caps.conditional_field, ARM_CC_NE - 1)

    def test_opcode_field(self):
        caps = CAPSInstruction(0xe52de004, 0x10550)  # str;lr, [sp, #-4]!
        self.assertEqual(caps.opcode_field, ARM_INS_STR)

        caps = CAPSInstruction(0xe28cca10, 0x10550) # add ip, ip, #0x10000
        self.assertEqual(caps.opcode_field, ARM_INS_ADD)

        caps = CAPSInstruction(0x18bd8010, 0x10550) # popne;{r4, pc}
        self.assertEqual(caps.opcode_field, ARM_INS_POP)

    def test_registers_used(self):
        # TODO: Change from capstone registers numbers to my register numbers
        caps = CAPSInstruction(0xe52de004, 0x10550)  # str lr, [sp, #-4]!
        regs = caps.registers_used()
        self.assertEqual(2, len(regs))
        self.assertTrue(AReg.LR in regs and AReg.SP in regs)

        caps = CAPSInstruction(0x106f4, 0x10550) # strdeq r0, r1, [r1], -r4
        regs = caps.registers_used()
        self.assertEqual(3, len(regs))
        self.assertTrue(AReg.R0 in regs and AReg.R1 in regs and AReg.R4 in regs)

        caps = CAPSInstruction(0x18bd8010, 0x10550) # popne {r4, pc}
        regs = caps.registers_used()
        self.assertEqual(3, len(regs))
        self.assertTrue(AReg.R4 in regs and AReg.PC in regs and AReg.SP in regs)

    def test_registers_written(self):
        caps = CAPSInstruction(0x18bd8010, 0x10550)  # popne {r4, pc}
        regs = caps.registers_written()
        self.assertEqual(3, len(regs))
        self.assertTrue(AReg.SP in regs and AReg.R4 in regs and AReg.PC in regs)

        caps = CAPSInstruction(0xe92d4800, 0x10550) # push {fp, lr}
        regs = caps.registers_written()
        self.assertEqual(0, len(regs))

    def test_registers_read(self):
        # TODO: Change from capstone registers numbers to my register numbers
        caps = CAPSInstruction(0xe52de004, 0x10550)  # str lr, [sp, #-4]!
        regs = caps.registers_read()
        self.assertEqual(1, len(regs))
        self.assertTrue(AReg.SP in regs)

        caps = CAPSInstruction(0x106f4, 0x10550) # strdeq r0, r1, [r1], -r4
        regs = caps.registers_read()
        self.assertEqual(2, len(regs))
        self.assertTrue(AReg.R1 in regs and AReg.R4 in regs)

        caps = CAPSInstruction(0x18bd8010, 0x10550) # popne {r4, pc}
        regs = caps.registers_read()
        self.assertEqual(1, len(regs))
        self.assertTrue(AReg.SP in regs)

        caps = CAPSInstruction(0xe92d4800, 0x10550) # push {fp, lr}
        regs = caps.registers_read()
        self.assertEqual(3, len(regs))
        self.assertTrue(AReg.SP in regs and AReg.FP in regs and AReg.LR in regs)

    def test_is_branch(self):
        self.assertTrue(CAPSInstruction(0xe5bef008, 0x10550).is_branch)  # ldr pc, [lr, #8]!
        self.assertTrue(CAPSInstruction(0xebffffeb, 0x10550).is_branch) # bl #0x105ac

    def test_is_push_pop(self):
        self.assertTrue(CAPSInstruction(0x18bd8010, 0x10550).is_push_pop)  # popne {r4, pc}
        self.assertTrue(CAPSInstruction(0xe92d4010, 0x10550).is_push_pop)  # push {r4, lr}

    def test_is_a(self):
        self.assertTrue(CAPSInstruction(0x18bd8010, 0x10550).is_a('pop'))  # popne {r4, pc}
        self.assertTrue(CAPSInstruction(0xe92d4010, 0x10550).is_a('push'))  # push {r4, lr}
        self.assertTrue(CAPSInstruction(0x106f4, 0x10550).is_a('str'))  # strdeq r0, r1, [r1], -r4
        self.assertTrue(CAPSInstruction(0xe28cca10, 0x10550).is_a('add')) # add ip, ip, #0x10000

    #def test_jumping_address(self):
        #CAPSInstruction(0xebffffeb, 0x10550)
    #   self.fail()

    def test_modifies_flags(self):
        self.assertTrue(CAPSInstruction(0xe3530000, 0x10550).modifies_flags()) # cmp r3, #0
        self.assertFalse(CAPSInstruction(0xe28cca10, 0x10550).modifies_flags()) # add ip, ip, #0x10000

#    def test_encodings_to_inst(self):
#        self.fail()
