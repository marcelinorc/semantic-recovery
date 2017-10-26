from unittest import TestCase

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader, ElfioTextDisassembleReader
from semantic_codec.corruption.corruptors import RandomCorruptor, CAPSInstruction
from semantic_codec.metadata.metadata_collector import MetadataCollector
from semantic_codec.metadata.probabilistic_rules.rules import from_instruction_list_to_dict
from semantic_codec.solution.solution_builders import ForwardConstraintSolutionBuilder, \
    ForwardConstraintSolutionEnumerator
from semantic_codec.solution.solution_quality import SolutionQuality
from tests.test_disassembler_readers import TestTextDisassembleReader


class TestForwardConstraintSolutionBuilder(TestCase):

    @staticmethod
    def obtain_corrupted_program():
        # Obtain a program and corrupt it
        instructions = ElfioTextDisassembleReader("data/helloworld_elfiodissasembly.disam").read()[1]
        collector = MetadataCollector()
        collector.collect(instructions)
        corruptor = RandomCorruptor(30.0, 5, True)
        corruptor.save_corrupted_program = False
        program = [CAPSInstruction(x.encoding, x.address) for x in instructions]
        program = corruptor.corrupt(from_instruction_list_to_dict(program))
        return instructions, program

    def initialize_test(self):
        instructions, program = TestForwardConstraintSolutionBuilder.obtain_corrupted_program()
        # Obtain the answer size before any constraint building
        a = SolutionQuality(program, instructions)
        a.report()

        return a, program, instructions

    def test_index_solution(self):
        a, program, instructions = self.initialize_test()
        b = ForwardConstraintSolutionEnumerator(program, instructions)
        b.build()
        print('Solution Index: {}'.format(b.solution))
        print('After Constrainst Size {} - Original Size {}'.format(b.solution_size, a.solution_size))
        self.assertIsNotNone(b.solution)
        self.assertGreaterEqual(a.solution_size, b.solution_size)

    def test_build_solution(self):
        a, program, instructions = self.initialize_test()
        # Build the forward constaints
        b = ForwardConstraintSolutionBuilder(program, instructions)
        b.build()
        print('After Constrainst Size {} - Original Size {}'.format(b.solution_size, a.solution_size))
        self.assertGreaterEqual(a.solution_size, b.solution_size)
