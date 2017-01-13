import os
from unittest import TestCase

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.metadata.collector import MetadataCollector
from semantic_codec.metadata.rules import from_instruction_list_to_dict, ConditionalFollowsCPSRModifier
from tests.corruptor import corrupt_instruction


class TestRule(object):

    class Common (TestCase):

        ASM_PATH = os.path.join(os.path.dirname(__file__), 'data/dissasembly.armasm')

        def assert_original_has_good_score(self, original, candidates, recovers=False):
            if recovers:
                self.assertTrue(original.score() > 0)
                for i in range(1, len(candidates)):
                    c = candidates[i]
                    self.assertTrue(original.score() > c.score(),
                                    "ORIGINAL {} : {} - CANDIDATE {} : {}".format(original, original.score(), c, c.score()))
            else:
                self.assertTrue(original.score() >= 0)
                for i in range(1, len(candidates)):
                    c = candidates[i]
                    self.assertTrue(original.score() >= c.score(),
                                    "ORIGINAL {} : {} - CANDIDATE {} : {}".format(original, original.score(), c, c.score()))

        @staticmethod
        def get_original_instruction(path, address, needs_collector):
            if needs_collector:
                program = TextDisassembleReader(path).read()
                collector = MetadataCollector()
                collector.collect(program)
                program = from_instruction_list_to_dict(program)
                return program[address][0], program, collector
            else:
                program = from_instruction_list_to_dict(TextDisassembleReader(path).read())
                return program[address][0], program, None

        def do_test(self, address, rule, recover_instruction, needs_collector=False,
                    path=ASM_PATH, corrupt_conditional=True, corrupt_registers=False, corrupt_opcode=False):
            # We start with the original program
            original_instruction, program, collector = self.get_original_instruction(path, address, needs_collector)
            # We corrupt it
            corrupt_instruction(program, original_instruction, address,
                                corrupt_conditional, corrupt_registers, corrupt_opcode)
            # We recover it
            if needs_collector:
                updated = rule(program, collector=collector).recover(address)
            else:
                updated = rule(program).recover(address)
            # Assert stuff
            self.assertTrue(updated)
            self.assert_original_has_good_score(original_instruction, program[address], recover_instruction)
