"""
Readers of disassemble files
"""
import re

from semantic_codec.architecture.capstone_instruction import CAPSInstruction
from semantic_codec.architecture.functions import ElfFunction
from semantic_codec.architecture.instruction import Instruction


class DisassembleReader (object):
    """
    Abstract class of all disassemble file readers
    """

    ARM_SET = 0
    THUMB_SET = 1
    BOTH = 2

    def __init__(self, filename, instruction_set=ARM_SET):
        self._filename = filename
        self._instruction_set = instruction_set

    def read_instructions(self):
        """
        Read a disassemble file
        :return: A list of instructions sorted by their memory address
        """
        pass

    @staticmethod
    def _disassemble(encodings, instruction_set=ARM_SET):
        """
        Disassemble a list of instructions
        """
        pass


class ElfioTextDisassembleReader(DisassembleReader):

    def __init__(self, filename, instruction_set=DisassembleReader.ARM_SET):
        super(ElfioTextDisassembleReader, self).__init__(filename, instruction_set)
        self.functions = None
        self.instructions = None

    def read(self):

        functions = {}

        current_fn = None

        self.instructions = []
        section = None
        for line in open(self._filename):
            if line.strip() == "":
                continue
            elif line.startswith('.'):
                section = line.split(".")[1]
            else:
                if section.startswith('function'):
                    address, name = line.split(';')
                    functions[int(address, 16)] = ElfFunction(name.rstrip())
                elif section.startswith('init') or section.startswith('text') or \
                        section.startswith('plt') or section.startswith('fini'):
                    line_split = line.split(';')
                    try:
                        address, encoding = line_split[0], line_split[1]
                    except:
                        print('[ERROR] Cannot parse line: {}'.format(line))
                        continue
                    encoding = int(encoding, 16)
                    address = int(address, 16)
                    inst = CAPSInstruction(encoding, position=address)
                    if address in functions:
                        current_fn = functions[address]
                    if current_fn:
                        current_fn.instructions.append(inst)
                    self.instructions.append(inst)

        self.functions = [x for x in functions.values()]

        return self.functions, self.instructions

    def read_functions(self):
        return self.read()[0]

    def read_instructions(self):
        return self.read()[1]

class TextDisassembleReader(DisassembleReader):
    """
    Reads the instructions in text format from the https://onlinedisassembler.com/static/home/,
    for example:    .text:000107ec f0 87 bd e8
    """
    def __init__(self, filename, instruction_set=DisassembleReader.ARM_SET):
        super(TextDisassembleReader, self).__init__(filename, instruction_set)
        self.functions = None
        self.instructions = None

    def read_functions(self):
        # Function header in our assembly
        p = re.compile("^\.\w+\:[0-9a-f]+\s*\<[\$|\w+]")

        if self._instruction_set != DisassembleReader.ARM_SET:
            raise RuntimeError("Instruction encoding not supported yet")

        result = []

        k, i = "no_method", 0
        result.append(ElfFunction(k))
        for line in open(self._filename):
            line = line.rstrip('\n')
            if p.match(line):
                k = line
                if k in result:
                    i += 1
                    k = line + i
                result.append(ElfFunction(k))
            elif len(line) > 0 and line[0] == ' ':
                e = line.split(":", 1)[1].split("  ", 1)[0].split(" ", 1)
                f = result[len(result) - 1]
                encoding = Instruction.reverse_endianess(e[1])
                f.instructions.append(CAPSInstruction(encoding, position=int(e[0], 16)))

        return result

    def read(self):
        return (self.read_instructions(), self.read_functions())

    def read_instructions(self):
        if self._instruction_set != DisassembleReader.ARM_SET:
            raise RuntimeError("Instruction encoding not supported yet")

        result = []

        for line in open(self._filename):
            if line[0] == ' ':
                e = line.rstrip('\n').split(":", 1)[1].split("  ", 1)[0].split(" ", 1)
                encoding = Instruction.reverse_endianess(e[1])
                instruction = CAPSInstruction(encoding, position=int(e[0], 16))
                result.append(instruction)

        return result