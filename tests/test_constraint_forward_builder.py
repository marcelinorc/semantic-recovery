from unittest import TestCase

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.corruption.corruptors import RandomCorruptor, DARMInstruction
from semantic_codec.metadata.answer_quality import AnswerQuality
from semantic_codec.metadata.constraints_recuperator import ProblemBuilder, ForwardConstraintSolutionBuilder, \
    ForwardConstraintSolutionEnumerator
from semantic_codec.metadata.collector import MetadataCollector
from semantic_codec.metadata.rules import from_instruction_list_to_dict
from tests.test_disassembler_readers import TestTextDisassembleReader


class TestForwardConstraintSolutionBuilder(TestCase):

    def initialize_test(self):
        # Obtain a program and corrupt it
        instructions = TextDisassembleReader(TestTextDisassembleReader.ASM_PATH).read_instructions()
        collector = MetadataCollector()
        collector.collect(instructions)
        corruptor = RandomCorruptor(30.0, 5, True)
        corruptor.save_corrupted_program = False
        program = [DARMInstruction(x.encoding, x.position) for x in instructions]
        program = corruptor.corrupt(from_instruction_list_to_dict(program))

        # Obtain the answer size before any constraint building
        a = AnswerQuality(program, instructions)
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
