from semantic_codec.corruption.corruption import *
from semantic_codec.interleaver.interleaver2d import build_2d_interleave_sp
from semantic_codec.report.print_progress import TextProgressBar


class Corruptor(object):

    def __init__(self):
        self.save_corrupted_program = False
        self.corrupted_program_path = None

    def corrupt(self, program):
        pass

    def _save_corrupted_program(self, program):
        if not self.corrupted_program_path:
            raise RuntimeError('Cannot save program, path is undefined')
        else:
            save_corrupted_program_to_json(program, self.corrupted_program_path)


class JSONCorruptor(Corruptor):
    """
    Loads a corrupted program from a JSON file
    """

    def __init__(self, path=None):
        super(JSONCorruptor).__init__()
        self.corrupted_program_path = path

    def corrupt(self, program):
        if not self.corrupted_program_path:
            raise RuntimeError('Cannot load corrupted program. No path is set')
        return load_corrupted_program_from_json(self.corrupted_program_path)


class PacketCorruptor(Corruptor):
    """
    Simulates the effect of packet losses to corrupt a program.

    The corruptor assumes that the program have been interleaved using the results by Zhang:

    "A new two-dimensional interleaving technique using successive packing"
    """
    def __init__(self, packet_count=None, data_size=None, interleave=None,
                 packets_lost=None, bits_per_interleave=2, save_corrupted_path=None):
        super(PacketCorruptor, self).__init__()
        self.packet_count = math.ceil(packet_count) # Just in case
        self.data_size = data_size
        self.interleave = interleave
        self.packet_lost = packets_lost
        self.bits_per_interleave = bits_per_interleave
        self.save_corrupted_program = save_corrupted_path is not None
        self.corrupted_program_path = save_corrupted_path

    def _corrupt_address(self, tuples, address, program):
        corrupted = []
        for inst in program[address]:
            for c_inst in corrupt_all_bits_tuples(tuples, inst.encoding):
                arm_inst = CAPSInstruction(c_inst, program[address][0].address)
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

        # TODO: This is a bottleneck created by the badly choosen representation of data
        addresses = [x for x in program.keys()]
        addresses.sort()
        # predict packet losses
        errors = predict_corruption(self.packet_count, self.bits_per_interleave, self.data_size,
                                    self.interleave, self.packet_lost)
        # Make sure all errors of a same byte are grouped together
        vv = len(errors) * 100
        errors.sort(key=lambda x: x[0] * vv + x[1])

        # Corrupt the program
        k, tuples, e = 0, [], errors[0]
        current = e[0]

        # Create a nice progress bar. TODO: Factor this out so other widgets can be used as well.
        progress_bar = TextProgressBar(iteration=0, total=len(errors),
                                       prefix='Corrupting:',
                                       decimals=0, bar_length=50, print_dist=4)

        while k <= len(errors):
            if current != e[0] or k == len(errors):
                if len(tuples) != 0 and current < len(addresses):
                    address = addresses[current]
                    self._corrupt_address(tuples, address, program)
                    tuples = []
                current = e[0]

            # Some errors expand through different bytes and are represented by a three index tuple
            if len(e) == 2:
                tuples.append((e[1], e[1] + self.bits_per_interleave))
            else:
                tuples.append((e[1], e[1] + e[2]))

            k += 1
            if k < len(errors):
                e = errors[k]

            # Progress the bar. TODO: Factor this out so other widgets can be used as well.
            progress_bar.progress()

        for v in program.values():
            v.sort(key=lambda x : x.encoding)

        if self.save_corrupted_program:
            self._save_corrupted_program(program)

        return program

class RandomCorruptor(Corruptor):
    """
    Corrupts a random set of bits in a program
    """
    def __init__(self, corrupted_percent=20, max_error_per_instruction=3, save_corrupted=True):
        super(RandomCorruptor, self).__init__()
        self.corrupted_percent = corrupted_percent
        self.max_error_per_instruction = max_error_per_instruction
        self.save_corrupted_program = save_corrupted

    def corrupt(self, program):
        corrupt_program(program, self.corrupted_percent, self.max_error_per_instruction)
        if self.save_corrupted_program:
            self._save_corrupted_program(program)
        return program
