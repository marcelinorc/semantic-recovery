from semantic_codec.metadata.probabilistic_rules.counting_rules import ConditionalCount, RegisterCount, InstructionCount
from tests.TestRule import TestRule


class TestConditionalCount(TestRule.Common):

    def test_recover_ConditionalCount(self):
        self.do_test(address=0x000107bc, rule=ConditionalCount, needs_collector=True, recover_instruction=True)

    def test_recover_RegisterCount(self):
        self.do_test(address=0x000107ac, rule=RegisterCount, needs_collector=True, recover_instruction=False,
                     corrupt_conditional=False,
                     corrupt_registers=True)

    def test_recover_InstructionCount(self):
        self.do_test(address=0x000107ac, rule=InstructionCount, needs_collector=True, recover_instruction=False,
                     corrupt_conditional=False,
                     corrupt_opcode=True)
