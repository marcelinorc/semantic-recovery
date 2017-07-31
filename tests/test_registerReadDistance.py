from semantic_codec.metadata.probabilistic_rules.distance_rule import RegisterReadDistance
from tests.TestRule import TestRule


class TestRegisterReadDistance(TestRule.Common):

    def test_recover(self):
        self.do_test(address=0x000107ac, rule=RegisterReadDistance, needs_collector=True, recover_instruction=False,
                     corrupt_conditional=False,
                     corrupt_registers=True)
