import re
from metadata.bits import Bits


class Instruction(object):
    """
    Class representing an instruction
    """

    # Instruction is given as an hexadecimal string
    HEX_STR = 16
    # Instruction is given as a decimal number
    DEC_STR = 10

    def __init__(self, encoding, str_format=DEC_STR, little_endian=True, position=0):
        self._position = position
        if isinstance(encoding, str):
            encoding = re.sub(' +', '', encoding)
            if little_endian and str_format == Instruction.HEX_STR:
                encoding = Instruction._reverse_endianess(encoding)
            self._encoding = int(encoding, str_format)
        elif isinstance(encoding, int):
            self._encoding = encoding
        else:
            raise RuntimeError("The Opcode must be an string or an integer value")

        self._ssa_read = []
        self._ssa_written = []

        self._jumping_address = None

        # If this is a "branch with link" instruction this points to the instruction to return to
        self.link_instruction = None

    @property
    def jumping_address(self):
        """
        Jumping address for branching instructions
        """
        return self._jumping_address

    @property
    def ssa_read(self):
        """
        Single Static Assignment renaming of the registers read
        """
        return self._ssa_read

    @property
    def ssa_written(self):
        """
        Single Static Assignment renaming of the registers written
        """
        return self._ssa_written

    @staticmethod
    def _get_register_list(encoding):
        result = []
        for x in range(0, 16):
            if Bits.is_on(encoding, x) and x not in result:
                result.append(x)
        return result

    @staticmethod
    def _reverse_endianess(value):
        a = list(value)
        l = [a[6:8], a[4:6], a[2:4], a[0:2]]
        return ''.join([item for sublist in l for item in sublist])

    @property
    def encoding(self):
        return self._encoding

    @property
    def position(self):
        """
        Memory position of the instruction
        """
        return self._position

    def registers_used(self):
        pass

    def registers_read(self):
        pass

    def registers_written(self):
        pass

    @property
    def is_branch(self):
        """
        Determine if an instruction is branch
        """
        pass

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
            if self.jumping_address == i.position:
                return i
        return None

