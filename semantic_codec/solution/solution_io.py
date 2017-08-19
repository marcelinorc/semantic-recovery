import struct

from semantic_codec.architecture.capstone_instruction import CAPSInstruction
from semantic_codec.metadata.probabilistic_rules.rules import from_instruction_list_to_dict


class SolutionReader(object):

    def read_long(self, fin):
        return struct.unpack('<Q', fin.read(8))[0]

    def read_int(self, fin):
        return struct.unpack('<L', fin.read(4))[0]

    def read(self, file_name):

        fin = open(file_name, 'rb')

        magic_word = self.read_long(fin)

        if magic_word != SolutionWriter.MAGIC_WORD:
            raise RuntimeError('The file is not a binary solution file')

        program = {}
        original = {}

        try:
            addr_count = self.read_int(fin)
            for i in range(0, addr_count):
                addr = self.read_int(fin)
                count = self.read_int(fin)
                if count > 0:
                    program[addr] = [CAPSInstruction(self.read_int(fin), addr) for j in range(0, count)]
                    original[addr] = [CAPSInstruction(program[addr][count - 1].encoding, addr)]
        finally:
            fin.close()

        return original, program


class SolutionWriter(object):

    MAGIC_WORD = 0xA0C1E2F3A4C5E6F7

    def write_long(self, fout, value):
        fout.write(struct.pack('<Q', value))

    def write_int(self, fout, value):
        fout.write(struct.pack('<L', value))

    def write_binary(self, file_name, original_program, program):

        if original_program.__class__ is list:
            original_program = from_instruction_list_to_dict(original_program)

        fout = open(file_name, 'wb')

        self.write_long(fout, SolutionWriter.MAGIC_WORD)

        try:
            self.write_int(fout, len(program))
            for k, v in program.items():
                self.write_int(fout, k)
                ori = -1
                index = 0

                # Search for all the instructions in the address which one is the original
                for vv in v:
                    if vv.encoding == original_program[k][0].encoding:
                        ori = index
                        # What's the point of storing bad solutions?
                        break
                    index += 1

                # If we reach the end without finding the original, something weird happen
                if index == len(v):
                    raise RuntimeError("This address does not contains the original instruction.")

                self.write_int(fout, ori + 1)
                for i in range(0, ori + 1):
                    self.write_int(fout, v[i].encoding)
        finally:
            fout.close()