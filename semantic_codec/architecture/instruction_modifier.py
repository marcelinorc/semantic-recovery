from semantic_codec.architecture.bits import Bits


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

    def modify_rn(self, inst, rn):
        """
        Modifies the Rn register in an instruction
        :param inst: Instruction to modify
        :param Rn: The new register
        :return: The modified instruction
        """
        return Bits.copy_bits(rn, inst, 0, 3, 16)

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
        #instruction.
        pass