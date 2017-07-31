from unittest import TestCase

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.corruption.corruptors import RandomCorruptor
from semantic_codec.metadata.metadata_collector import MetadataCollector
from semantic_codec.metadata.probabilistic_rules.rules import from_instruction_list_to_dict
from semantic_codec.metadata.solution_builders import ProblemBuilder
from tests.test_disassembler_readers import TestTextDisassembleReader


class TestProblemBuilder(TestCase):

    def test_build(self):
        instructions = TextDisassembleReader(TestTextDisassembleReader.ASM_PATH).read_instructions()

        collector = MetadataCollector()
        collector.collect(instructions)

        corruptor = RandomCorruptor(10.0, 2, True)
        corruptor.save_corrupted_program = False
        instructions = corruptor.corrupt(from_instruction_list_to_dict(instructions))

        problem = ProblemBuilder().build(instructions, collector)

        c = 1
        for k, v in instructions.items():
            c *= len(instructions[k])

        print('Initial solutions: {}'.format(c))

        solutions = problem.getSolutions()

        print('After constraints solutions: {}'.format(len(solutions)))


        #for x in range(1, min(4, len(solutions))):
        #    print('---------------')
        #    for v in solutions[x]:
        #        print('{} : {}'.format(v, str(solutions[x][v])))

        self.assertGreaterEqual(c, len(solutions))
