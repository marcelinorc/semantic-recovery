from semantic_codec.architecture.arm_constants import AOpType, AOp
from semantic_codec.architecture.bits import Bits
from semantic_codec.architecture.instruction import Instruction



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


