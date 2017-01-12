import os
from unittest import TestCase

from semantic_codec.architecture.darm_instruction import DARMInstruction
from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.metadata.rules import ConditionalFollowsCPSRModifier, from_instruction_list_to_dict
from tests.corruptor import corrupt_conditional, corrupt_instruction


class TestConditionalFollowsCPSRModifier(TestCase):
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
    def get_original_instruction(path, address):
        program = from_instruction_list_to_dict(TextDisassembleReader(path).read())
        return program[address][0], program

    def do_test(self, address, recover_instruction, path=ASM_PATH):
        # We start with the original program
        ADDRESS = address  # 0x000107cc # points to: add r4, r4, #1
        original_instruction, program = self.get_original_instruction(path, ADDRESS)
        # We corrupt it
        corrupt_instruction(program, original_instruction, ADDRESS)
        # We recover it
        updated = ConditionalFollowsCPSRModifier(program).recover(ADDRESS)
        # Assert stuff
        self.assertTrue(updated)
        self.assert_original_has_good_score(original_instruction, program[ADDRESS], recover_instruction)

    def test_recover_surrounded(self):
        """
        Test the recovery of an instruction after a flag changer
        :return:
        """
        self.do_test(address=0x00010614, recover_instruction=True, path='data/helloworld.armasm')

    def test_keep_after_flag_update(self):
        """
        Test the recovery of an instruction after a flag changer
        :return:
        """
        self.do_test(address=0x000107bc, recover_instruction=False)

    def test_recover_is_always(self):
        """
        Test the recovery of an easy 'always conditional' instruction
        """
        # We start with the original program
        self.do_test(address=0x000107cc, recover_instruction=True)  # points to: add r4, r4, #1
