import struct
import sys
from semantic_codec.architecture.bits import Bits
from semantic_codec.architecture.capstone_instruction import CAPSInstruction
from libs.darm import darm



class InstructionModifier(object):
    """
    Modifies parts of an instruction such as its conditional, operand, etc.
    """
    def modify_cond(self, inst, new_cond):
        """
        Modifies an instructions conditional
        :param inst: Instruction to modify
        :param new_cond: New conditional
        :return: The modified instruction
        """
        return Bits.copy_bits(new_cond, inst, 0, 3, 28)

    def modify_opcode(self, inst, new_cond):
        """
        Modifies an instructions conditional
        :param inst: Instruction to modify
        :param new_cond: New conditional
        :return: The modified instruction
        """
        return Bits.copy_bits(new_cond, inst, 0, 3, 21)

    def modify_rn(self, encoding, rn):
        """
        Modifies the Rn register in an instruction
        :param encoding: Instruction to modify
        :param Rn: The new register
        :return: The modified instruction
        """
        return Bits.copy_bits(rn, encoding, 0, 3, 16)

    def modify_rd(self, inst, rd):
        """
        Modifies the Rd register in an instruction
        :param inst: Instruction to modify
        :param Rd: The new register
        :return: The modified instruction
        """
        return Bits.copy_bits(rd, inst, 0, 3, 12)

    def modify_rs(self, inst, rs):
        """
        Modifies the Rd register in an instruction
        :param inst: Instruction to modify
        :param Rd: The new register
        :return: The modified instruction
        """
        return Bits.copy_bits(rs, inst, 0, 3, 8)

    def modify_rm(self, inst, rs):
        """
        Modifies the Rd register in an instruction
        :param inst: Instruction to modify
        :param Rd: The new register
        :return: The modified instruction
        """
        return Bits.copy_bits(rs, inst, 0, 3, 0)

    def modify_immediate(self, inst, immediate):
        """
        Modify the immediate in an instruction
        :param inst: Instruction to modify
        :param inmediate: The new Immediate
        :return:
        """
        if inst & 0xE000000 == 0x4000000:
            return Bits.copy_bits(immediate, inst, 0, 11, 0)
        else:
            return Bits.copy_bits(immediate, inst, 0, 7, 0)



    def modify_register(self, instruction, register, new_reg):
        # Flip endianes.
        encoding = instruction.encoding
        swe = self.swap23(encoding)
        # DARM instructions came handy as they provide Rn, RD, RM and RS registers
        d = darm.disasm_armv7(swe)

        if d.Rn and register == d.Rn.idx:
            encoding = self.modify_rn(swe, new_reg)
        elif d.Rd and register == d.Rd.idx:
            encoding = self.modify_rd(swe, new_reg)
        elif d.Ra and register == d.Ra.idx:
            encoding = self.modify_rn(swe, new_reg) # Not a bug Rt and Rd lives in same bits
        elif d.Rt and register == d.Rt.idx:
            encoding = self.modify_rd(swe, new_reg) # Not a bug Rt and Rd lives in same bits
        elif d.Rs and register == d.Rs.idx:
            encoding = self.modify_rs(swe, new_reg)
        elif d.Rm and register == d.Rm.idx:
            encoding = self.modify_rm(swe, new_reg)
        elif d.reglist.reglist > 0 and register in d.reglist.reglist:
            encoding = self.modify_register_list(instruction, register, new_reg)

        #encoding = self.swap23(encoding)

        return encoding, register in CAPSInstruction(encoding, 0).registers_used()

    def modify_register_list(self, instruction, register, new_reg):
        encoding = self.swap23(instruction.encoding)
        if instruction.is_push_pop():
            encoding &= 2 ** register
            encoding |= 2 ** new_reg
            return encoding
        else:
            raise RuntimeError('Not a register list instruction')