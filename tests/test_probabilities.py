from unittest import TestCase

from semantic_codec.probability.probabilities import indep_events_union


class TestUnion(TestCase):

    def test_union(self):
        self.assertEqual(0.72, indep_events_union([0.2, 0.3, 0.5]))
