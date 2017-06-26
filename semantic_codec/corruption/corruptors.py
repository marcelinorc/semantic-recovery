from semantic_codec.corruption.corruption import *
from semantic_codec.interleaver.interleaver2d import build_2d_interleave_sp


class Corruptor(object):
    def corrupt(self, program):
        pass


class JSONCorruptor(Corruptor):
    """
    Loads a corrupted program from a JSON file
    """

    def __init__(self, path):
        self.corrupted_program = path

    def corrupt(self, program):
        return load_corrupted_program_from_json(self.corrupted_program)


class PacketCorruptor(Corruptor):
    """
    Simulates the effect of packet losses to corrupt a program.

    The corruptor assumes that the program have been interleaved using the results by Zhang:

    "A new two-dimensional interleaving technique using successive packing"
    """
    def __init__(self, packet_count=None, data_size=None, interleave=None, packets_lost=None, bits_per_interleave=2):
        self.packet_count = math.ceil(packet_count) # Just in case
        self.data_size = data_size
        self.interleave = interleave
        self.packet_lost = packets_lost
        self.bits_per_interleave = bits_per_interleave

    def _corrupt_address(self, tuples, address, program):
        corrupted = []
        for inst in program[address]:
            for c_inst in corrupt_all_bits_tuples(tuples, inst.encoding):
                arm_inst = DARMInstruction(c_inst, program[address][0].position)
                if not arm_inst in corrupted:
                    corrupted.append(arm_inst)
        program[address] = corrupted

    def corrupt(self, program):
        """
        Simulates the effect of packet losses to corrupt a program.
        :param program: A dictionary of {address => DARMInstructions}
        :return: The program corrupted in the form of {address => [DARMInstructions]}
        """
        if not self.packet_lost:
            raise RuntimeError('No packet lost information. Cannot corrupt')

        if not self.interleave:
            self.interleave = build_2d_interleave_sp(self.packet_count, True)

        addresses = [x for x in program.keys()] # TODO: This is a bottleneck created by the badly choosen representation of data
        addresses.sort()
        # predict packet losses
        errors = predict_corruption(self.packet_count, self.bits_per_interleave, self.data_size,
                                    self.interleave, self.packet_lost)
        # Make sure all errors a together
        vv = len(errors) * 100
        errors.sort(key=lambda x: x[0] * vv + x[1])

        # Corrupt the program
        k, tuples, e = 0, [], errors[0]
        current = e[0]
        while k <= len(errors):
            if current != e[0] or k == len(errors):
                if len(tuples) != 0 and current < len(addresses):
                    address = addresses[current]
                    self._corrupt_address(tuples, address, program)
                    tuples = []
                current = e[0]
            if len(e) == 2:
                tuples.append((e[1], e[1] + self.bits_per_interleave))
            else:
                tuples.append((e[1], e[1] + e[2]))
            k += 1
            if k < len(errors):
                e = errors[k]


        return program

class RandomCorruptor(Corruptor):
    """
    Corrupts a random set of bits in a program
    """

    def __init__(self, corrupted_percent=20, max_error_per_instruction=3, corrupted_program=True):
        self.corrupted_percent = corrupted_percent
        self.max_error_per_instruction = max_error_per_instruction
        self.save_corrupted_program = corrupted_program

    def corrupt(self, program):
        corrupt_program(program, self.corrupted_percent, self.max_error_per_instruction)
        if self.save_corrupted_program:
            save_corrupted_program_to_json(program, "corrupted.json")
        return program
