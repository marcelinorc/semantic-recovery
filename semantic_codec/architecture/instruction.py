import re
import struct

from semantic_codec.architecture.arm_constants import AReg
from semantic_codec.architecture.bits import Bits


class Instruction(object):
    """
    Class representing an instruction
    """

    # Instruction is given as an hexadecimal string
    HEX_STR = 16
    # Instruction is given as a decimal number
    DEC_STR = 10

    def __init__(self, encoding, position, str_format=HEX_STR):
        # Endiannes of the data given to the instruction
        self._storages_used = None
        self._storages_read = None
        self._storages_written = None
        self._address = position
        self._ssa_read = []
        self._ssa_written = []
        self._jumping_address = None
        # If this is a "branch with link" instruction this points to the instruction to return to
        self.link_instruction = None
        # score of the instruction
        self.scores_by_rule = {}

        self.score_function = Instruction._add_score

        self._ignore = False

        if isinstance(encoding, str):
            self._encoding = int(''.join(encoding.split()), str_format)
#            encoding = re.sub(' +', '', encoding)
#           if little_endian and str_format == Instruction.HEX_STR:
#                encoding = Instruction._reverse_endianess(encoding)
        elif isinstance(encoding, int):
            self._encoding = encoding
        else:
            raise RuntimeError("The Opcode must be an string or an integer value")

    @staticmethod
    def _add_score(scores_by_rule, inst):
        result = 0
        for v in scores_by_rule.values():
            result += v
        return result

    def score(self):
        return self.score_function(self.scores_by_rule, self)

    @property
    def ignore(self):
        return self.is_undefined or self._ignore

    @ignore.setter
    def ignore(self, v):
        self._ignore = v

    @property
    def jumping_address(self):
        """
        Jumping address for branching instructions
        """
        if self.is_branch:
            if self._jumping_address is None:
                # On the other hand, one can compute the jumping address
                address = self.encoding & Bits.set(23, 0)
                if Bits.is_on(address, 23):
                    address |= Bits.set(29, 24)
                address = (address << 2)
                address += self.address + 8
                address &= 0xffffffff
                self._jumping_address = address
            return self._jumping_address
        return None

    @property
    def ssa_read(self):
        """
        Single Static Assignment renaming of the registers read_instructions
        """
        return self._ssa_read

    @property
    def ssa_written(self):
        """
        Single Static Assignment renaming of the registers written
        """
        return self._ssa_written

    @staticmethod
    def _get_register_list(encoding, result=None):
        if not result:
            result = []
        for x in range(0, 16):
            if Bits.is_on(encoding, x) and x not in result:
                result.append(x)
        return result

    @staticmethod
    def reverse_endianess(value):
        if isinstance(value, str):
            value = ''.join(value.split())
            a = list(value)
            l = [a[6:8], a[4:6], a[2:4], a[0:2]]
            return ''.join([item for sublist in l for item in sublist])
        elif isinstance(value, int):
            return struct.unpack("<I", struct.pack(">I", value))[0]

    @property
    def encoding(self):
        return self._encoding

    @property
    def address(self):
        """
        Memory address of the instruction
        """
        return self._address

    def _read_from_memory(self):
        pass

    def _writes_to_memory(self):
        pass

    def registers_used(self):
        pass

    def registers_read(self):
        pass

    def registers_written(self):
        pass

    def storages_used(self):
        """
        An storage is either a register or the system memory
        """
        if self._storages_used:
            return self._storages_used
        else:
            self._storages_used = []
            self._storages_used.extend(self.registers_used())
            if self._writes_to_memory() or self._read_from_memory():
                self._storages_used.append(16)
            if not self._storages_used:
                self._storages_used.append(18)  # The NOREG register. i.e. this instruction uses no register
            return self._storages_used

    def storages_written(self):
        """
        An storage is either a register or the system memory
        """
        if self._storages_written:
            return self._storages_written
        else:
            self._storages_written = []
            self._storages_written.extend(self.registers_written())
            if self._writes_to_memory():
                # 16 is the 'register' for memory
                self._storages_written.append(AReg.STORE)
            if 15 not in self._storages_written and self.is_branch:
                # PC counter
                self._storages_written.append(AReg.PC)
            return self._storages_written

    def storages_read(self):
        if self._storages_read:
            return self._storages_read
        else:
            self._storages_read = []
            self._storages_read.extend(self.registers_read())
            if self._read_from_memory():
                # 16 is the 'register' for memory
                self._storages_read.append(AReg.STORE)

            return self._storages_read

    @property
    def is_undefined(self):
        """
        Determine if an instruction is undefined
        """
        raise RuntimeError("Not implemented")

    @property
    def is_branch(self):
        """
        Determine if an instruction is branch
        """
        raise RuntimeError("Not implemented")

    def is_push_pop(self):
        """
        Determine if an instruction is a push or pop instructino
        """
        raise RuntimeError("Not implemented")

    @property
    def is_branch_with_link(self):
        return self.is_branch and (self.encoding & Bits.on(24))

    def branch_to(self, instructions):
        """
        Find the instruction where this instruction branchs to
        :param instructions: A list of instructions ordered by their address
        """
        # TODO: if needed replace this for a bin-search to increase performance
        for i in instructions:
            if self.jumping_address == i.address:
                return i
        return None

    def modifies_flags(self):
        pass
