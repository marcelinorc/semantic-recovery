import struct

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_BIG_ENDIAN
from capstone.arm_const import ARM_OP_REG, ARM_OP_MEM, ARM_INS_B, ARM_INS_BX, ARM_INS_BLX, ARM_INS_BL, ARM_INS_STR, \
    ARM_INS_STRBT, ARM_OP_IMM

from semantic_codec.architecture.arm_constants import AReg
from semantic_codec.architecture.instruction import Instruction

class CAPSInstruction(Instruction):

    def __init__(self, encoding, position):
        super(CAPSInstruction, self).__init__(encoding, position)
        # CAPSTONE object
        encoding_bytes = (self._encoding).to_bytes(4, byteorder='little')
        #endian = CS_MODE_LITTLE_ENDIAN if little_endian else CS_MODE_BIG_ENDIAN
        md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
        md.detail = True
        self._cap = None
        for i in md.disasm(encoding_bytes, position):
            self._cap = i


    def __str__(self):
        if not self._cap:
            return super(CAPSInstruction, self).__str__()
        return '{}\t{}'.format(self._cap.mnemonic, self._cap.op_str)




    @property
    def conditional_field(self):
        """
        Returns the conditional field of the instruction
        """
        return self._cap.cc - 1

    @property
    def opcode_field(self):
        """
        Returns the opcode
        """
        return self._cap.id

    @property
    def opcode_type(self):
        """
        Returns the type of the opcode
        """
        return self._cap.id

    def registers_used(self):
        """
        Returns registers used
        :return: A list of the index of the registers used
        """
        result = []
        if self.is_push_pop:
            result.append(AReg.SP)

        for i in self._cap.operands:
            if i.type == ARM_OP_REG:
                if i.value.reg not in AReg.CAPSTONE_REGS:
                    register = AReg.STORAGE_COUNT + i.value.reg
                else:
                    register = AReg.CAPSTONE_REGS[i.value.reg]
                if not register in result:
                    result.append(register)
            if i.type == ARM_OP_MEM:
                register = AReg.CAPSTONE_REGS[i.value.mem.base]
                if register != 0 and not register in result:
                    result.append(register)
                register = AReg.CAPSTONE_REGS[i.value.mem.index]
                if register != 0 and not register in result:
                    result.append(register)

        return result

    def registers_written(self):
        """
        Returns registers written
        :return: A list of the index of the registers written
        """
        if self.is_a('pop'):
            return self.registers_used()
        elif self.is_a('push'):
            return []
        else:
            return self.registers_used()[:1]

    def registers_read(self):
        """
        Returns registers read_instructions
        :return: A list of the index of the registers read_instructions
        """

        if self.is_a('pop'):
            result = []
        else:
            result = self.registers_used()[1:]

        if self.is_push_pop and not AReg.SP in result:
            result.append(AReg.SP)

        return result
        #result = []
        #if self._darm.Rn:
        #    result.append(self._darm.Rn.idx)
        #if self._darm.Rs:
        #    result.append(self._darm.Rs.idx)
        #if self._darm.Rm:
        #    result.append(self._darm.Rm.idx)

        #if self.conditional_field != AOpType.COND_ALWAYS:
        #    result.append(AReg.CPSR)

        #if self._inst_is('push'):
        #    if self._darm.reglist.reglist > 0:
        #        result.extend(Instruction._get_register_list(self._darm.reglist.reglist))

        #eturn result

    def _inst_is(self, inst):
        str_lw = str(self).lower()
        if type(inst) == list:
            for i in inst:
                if str_lw.startswith(i):
                    return True
        else:
            return str_lw.startswith(inst)

    def _writes_to_memory(self):
        # If its an store
        return ARM_INS_STR >= self._cap.id >= ARM_INS_STRBT

    def _read_from_memory(self):
        for op in self._cap.operands:
            if op.type == ARM_OP_MEM:
                return not self._writes_to_memory()
        return False


    @property
    def is_branch(self):
        """
        Return if the instruction is a branching instruction
        """
        return self.opcode_field in [ARM_INS_B, ARM_INS_BX, ARM_INS_BL, ARM_INS_BLX] or \
               AReg.PC in self.registers_written()

    @property
    def is_push_pop(self):
        return self._inst_is('push') or self._inst_is('pop')

    def is_a(self, value):
        return self._inst_is(value)

    @property
    def is_undefined(self):
        """
        Determine if an instruction is undefined
        """
        return not self._cap

    @property
    def jumping_address(self):
        """
        Jumping address for branching instructions
        """
        if self.is_branch:
            if self._jumping_address is None:
                for op in self._cap.operands:
                    if op.type == ARM_OP_IMM:
                        self._jumping_address = op.value.imm
                        break
                # On the other hand, one can compute the jumping address
                #address = self.encoding & Bits.set(23, 0)
                #if Bits.is_on(address, 23):
                #    address |= Bits.set(29, 24)
                #address = (address << 2)
                #address += self.address + 8
                #address &= 0xffffffff
                #self._jumping_address = address
            return self._jumping_address
        return None

    def modifies_flags(self):
        return self._cap.update_flags
        #return AReg.CPSR in self.storages_written()

    @staticmethod
    def encodings_to_inst(encodings, return_undefined=False):
        result = []
        for e in encodings:
            d = CAPSInstruction(e)
            if not d.is_undefined or return_undefined:
                result.append(d)
        return result
