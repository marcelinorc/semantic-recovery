from architecture.arm_instruction import AOpType, AReg
from architecture.bits import Bits
from architecture.instruction import Instruction
from darm import darm


class DARMInstruction(Instruction):
    """
    Wrapper instruction for the DARM disassembler
    """

    def __init__(self, encoding, str_format=Instruction.HEX_STR, little_endian=True, position=0):
        super().__init__(encoding, str_format, little_endian, position)
        self._darm = darm.disasm_armv7(self.encoding)

    def __str__(self):
        return str(self._darm) if self._darm else super().__str__()

    @property
    def darm(self):
        """
        Returns the Darm instruction being wrapped
        """
        return self._darm

    @property
    def conditional_field(self):
        """
        Returns the conditional field of the instruction
        """
        return self._darm.cond.idx

    @property
    def opcode_field(self):
        """
        Returns the opcode
        """
        return self._darm.instr.idx

    @property
    def opcode_type(self):
        """
        Returns the type of the opcode
        """
        return self._darm.instr_type.idx

    def registers_used(self):
        """
        Returns registers used
        :return: A list of the index of the registers used
        """
        result = self.registers_written()
        result.extend(self.registers_read())
        return result

    def registers_written(self):
        """
        Returns registers written
        :return: A list of the index of the registers written
        """

        result = []

        # special cases
        if self._inst_is(['tst', 'teq', 'cmp', 'cmn']):
            result.append(AReg.CPSR)
        if self._darm.Rt:
            result.append(self._darm.Rt.idx)
        if self._darm.Rd:
            result.append(self._darm.Rd.idx)
        if self._darm.reglist.reglist > 0 and not self._inst_is('push'):
            result.extend(Instruction._get_register_list(self._darm.reglist.reglist))
        return result

    def registers_read(self):
        """
        Returns registers read
        :return: A list of the index of the registers read
        """
        result = []
        if self._darm.Rn:
            result.append(self._darm.Rn.idx)
        if self._darm.Rs:
            result.append(self._darm.Rs.idx)
        if self._darm.Rm:
            result.append(self._darm.Rm.idx)

        if self.conditional_field != AOpType.COND_ALWAYS:
            result.append(AReg.CPSR)

        if self._inst_is('push'):
            if self._darm.reglist.reglist > 0:
                result.extend(Instruction._get_register_list(self._darm.reglist.reglist))

        return result

    def _inst_is(self, inst):
        str_lw = str(self._darm.instr).lower()
        if type(inst) == list:
            for i in inst:
                if i in str_lw:
                    return True
        else:
            return inst in str_lw

    def _writes_to_memory(self):
        # I'll use this cheap trick to avoid having to parse the instruction myself
        p = str(self._darm).split(',')
        return len(p) > 1 and ('[' in p[0] or ']' in p[0] or self._inst_is('push'))

    def _read_from_memory(self):
        # I'll use this cheap trick to avoid having to parse the instruction myself
        p = str(self._darm).split(',')
        return len(p) > 1 and (('[' in p[1] or ']' in p[1]) or self._inst_is('pop'))

    @property
    def is_branch(self):
        """
        Return if the instruction is a branching instruction
        """
        # The magic numbers 10 and 11 are due to the internal desing of the DARM library
        # see function "darm_enctype_name" in armv7.c
        return self._darm.instr_type.idx in [10, 11] or AReg.PC in self.registers_written()

    @property
    def is_undefined(self):
        """
        Determine if an instruction is undefined
        """
        return not self._darm

    @property
    def jumping_address(self):
        if self._jumping_address is None:
            # On the other hand, one can compute the jumping address
            address = self.encoding & Bits.set(23, 0)
            address = ((address | Bits.set(29, 24)) << 2) - Bits.on(32) if Bits.is_on(address, 23) else address
            address += self.position + 8
            self._jumping_address = address
        return self._jumping_address
