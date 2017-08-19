from unittest import TestCase

from semantic_codec.metadata.probabilistic_rules.rules import from_instruction_list_to_dict
from semantic_codec.solution.solution_io import SolutionWriter, SolutionReader
from tests.test_constraint_forward_builder import TestForwardConstraintSolutionBuilder


class TestSolutionWriter(TestCase):

    def check_equals(self, p1, p2):
        for k, v in p1.items():
            for vv in v:
                found = False
                for pp in p2[k]:
                    if vv.encoding == pp.encoding:
                        found = True
                        break
                self.assertTrue(found)

    def test_write_read_binary(self):
        original, program = TestForwardConstraintSolutionBuilder.obtain_corrupted_program()

        for v in program.values():
            v.sort(key=lambda x: x.encoding)

        writer = SolutionWriter()
        original = from_instruction_list_to_dict(original)
        writer.write_binary('data/data.sol', original, program)

        reader = SolutionReader()
        ori_readed, readed = reader.read('data/data.sol')

        # Check that readed is identical to written
        self.check_equals(readed, program)