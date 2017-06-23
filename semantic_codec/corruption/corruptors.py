from semantic_codec.corruption.corruption import *


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
    def __init__(self, ):
        pass


    def corrupt(self, program):
        pass



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
