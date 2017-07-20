from semantic_codec.architecture.bits import Bits
from semantic_codec.architecture.instruction import Instruction

class AReg:
    """
    ARM registers names. The cryptic AOp name is to have short code
    """
    R0 = 0
    R1 = A1 = 1
    R2 = A2 = 2
    R3 = A3 = 3
    R4 = V1 = 4
    R5 = V2 = 5
    R6 = V3 = 6
    R7 = WR = V4 = 7
    R8 = V5 = 8
    R9 = SB = V6 = 9
    R10 = SL = V7 = 10
    R11 = FP = V8 = 11
    R12 = IP = 12
    R13 = SP = 13
    R14 = LR = 14
    R15 = PC = 15
    # The store is modeled as a register
    STORE = 16
    # The flag register
    CPSR = 17
    # A fictitious register that is used to even the maths. The NOREG is the
    # register used by the instructions that use NO REGisters at all
    NOREG = 18

    STORAGE_NAMES = ["R{}".format(x) for x in range(0, 16)]
    STORAGE_NAMES.extend(['STORE', 'CPSR'])
    STORAGE_COUNT = len(STORAGE_NAMES)

class AOp(object):
    """
    ARM Opcodes and opcode types. The cryptic AOp name is to have short code
    """
    AND = 0b0000 << 21
    EOR = 0b0001 << 21
    SUB = 0b0010 << 21
    RSB = 0b0011 << 21
    ADD = 0b0100 << 21
    ADC = 0b0101 << 21
    SBC = 0b0110 << 21
    RSC = 0b0111 << 21
    TST = 0b1000 << 21
    TEQ = 0b1001 << 21
    CMP = 0b1010 << 21
    CMN = 0b1011 << 21
    ORR = 0b1100 << 21
    BIC = 0b1110 << 21
    MOV = 0b1101 << 21
    MVN = 0b1111 << 21


class AOpType(object):
    """
    ARM Opcodes types. The cryptic AOpType name is to have short code
    """
    ALWAYS = Bits.set(31, 29)
    COND_ALWAYS = 0b1110

    LOAD_STORE_MULTIPLE = Bits.on(27)
    LOAD_STORE = Bits.on(26)
    LOAD_STORE_OFFSET = Bits.set(26, 25)
    SOFT_INTERRUPT = 0xF000000
    BRANCH = 0xA000000
    DATA_PROCESSING = 0x0
    DATA_PROCESSING_IMMEDIATE = 0x2000000

class ARMInstruction(Instruction):
    """
    Class representing an ARM instruction.
    Don't use. Deprecated
    """

    INST_SIZE_BYTES = 4

    def conditional_field(self):
        """
        Return the condition part of the opcode for an ARM instruction (See the 'ARM ARM')
        :return:
        """
        return self.encoding & 0xF0000000

    def opcode_type(self):
        """
        Return the opcode type
        """
        return self.encoding & 0xE000000

    def opcode_field(self):
        """
        Return the instruction part of the opcode for an ARM instruction (See the 'ARM ARM')
        :return: A number with the instruction part
        """
        t = self.opcode_type()
        if t in [AOpType.BRANCH, AOpType.SOFT_INTERRUPT]:
            return t
        return self.encoding & Bits.set(24, 21)

    def _rn_field_(self):
        """
        Returns the Rn register field
        """
        return (self.encoding & Bits.set(19, 16)) >> 16

    def _rd_field_(self):
        """
        Returns the Rd register field
        """
        return (self.encoding & Bits.set(15, 12)) >> 12

    def _rs_field_(self):
        """
        Returns the Rd register field
        """
        return (self.encoding & Bits.set(11, 8)) >> 8

    def _rm_field_(self):
        """
        Returns the Rm register field
        """
        return self.encoding & 0xF

    def registers_used(self):
        """
        Returns the registers that this instruction is using
        :return: A list of numbers each one containing the index of the register
        """
        result = []
        t = self.opcode_type()

        # Data processing instructions
        if t <= AOpType.DATA_PROCESSING_IMMEDIATE:
            # Get the Rn register
            result.append(self._rn_field_())

            # Certain instructions address two registers:
            op = self.opcode_field()
            if op in range(AOp.EOR, AOp.RSC) or op in [AOp.AND, AOp.BIC, AOp.ORR]:
                result.append(self._rd_field_())

            # And others even three or four
            if t == AOpType.DATA_PROCESSING:
                result.append(self._rm_field_())
                if Bits.is_on(self.encoding, 4):
                    result.append(self._rs_field_())

        # Load and Store
        elif t in [AOpType.LOAD_STORE, AOpType.LOAD_STORE_OFFSET]:
            result.extend([self._rn_field_(), self._rd_field_()])
            if t == AOpType.LOAD_STORE_OFFSET:
                result.append(self._rm_field_())
        # Load and Store multiple
        elif t == AOpType.LOAD_STORE_MULTIPLE:
            result.append(self._rn_field_())
            result.extend(Instruction._get_register_list(self.encoding))

        return result

    def registers_written(self):
        """
        Returns the register written by the instruction
        """
        result = []
        t = self.opcode_type()
        # Data processing instructions
        if t in [AOpType.DATA_PROCESSING_IMMEDIATE, AOpType.DATA_PROCESSING, \
                 AOpType.LOAD_STORE, AOpType.LOAD_STORE_OFFSET]:
            result.append(self._rd_field_())
        # Load Store multiple
        if t == AOpType.LOAD_STORE_MULTIPLE:
            result.append(self._get_register_list())

        return result

    def registers_read(self):
        """
        Returns the registers read_instructions by the instruction
        """
        t = self.opcode_type()

        if t == AOpType.LOAD_STORE_MULTIPLE:
            return [self._rn_field_()]

        result = self.registers_used()
        result.remove(self._rd_field_())

        return result


