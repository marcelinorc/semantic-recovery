from semantic_codec.metadata.rules import ControlFlowBehavior
from tests.TestRule import TestRule


class TestConditionalFollowsCPSRModifier(TestRule.Common):

    def test_recover_surrounded(self):
        """
        Test the recovery of an instruction after a flag changer
        :return:
        """
        self.do_test(address=0x00010614, rule=ControlFlowBehavior,
                     recover_instruction=True, path='data/helloworld.armasm')

    def test_keep_after_flag_update(self):
        """
        Test the recovery of an instruction after a flag changer
        :return:
        """
        self.do_test(address=0x000107bc, rule=ControlFlowBehavior, recover_instruction=False)

    def test_recover_is_always(self):
        """
        Test the recovery of an easy 'always conditional' instruction
        """
        # We start with the original program
        self.do_test(address=0x000107cc, rule=ControlFlowBehavior, recover_instruction=True)  # points to: add r4, r4, #1
