import os
from unittest import TestCase

from semantic_codec.architecture.arm_instruction import AReg
from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.metadata.collector import MetadataCollector


class TestMetadataCollector(TestCase):

    ASM_PATH = os.path.join(os.path.dirname(__file__), 'data/dissasembly.armasm')

    def test_collect(self):
        instructions = TextDisassembleReader(self.ASM_PATH).read()
        # Collect the metadata
        c = MetadataCollector()
        c.collect(instructions)

        # Check the counting
        self.assertEqual(3, len(c.condition_count))

        """
        prev_inst = None
        for inst in c.empty_spaces:
            if prev_inst is None:
                print('{}; 0; {}'.format(inst.encoding, inst))
            else:
                print('{}; {}; {}'.format(inst.encoding, abs(prev_inst.encoding - inst.encoding), inst))
            prev_inst = inst
        """
        # Asser the max, mean, min distance between registers
        for i in range(0, AReg.STORAGE_COUNT):
            if i in c.storage_mean_dist:
                print("{}: {}, {}, {} ".format(i, c.storage_min_dist[i],
                                                     c.storage_mean_dist[i],c.storage_max_dist[i]))
                self.assertTrue(c.storage_min_dist[i] <= c.storage_mean_dist[i] <= c.storage_max_dist[i],
                                "{}: {}, {}, {} ".format(i, c.storage_min_dist[i],
                                                     c.storage_mean_dist[i],c.storage_max_dist[i]))