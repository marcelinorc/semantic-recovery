import os
from unittest import TestCase

from semantic_codec.architecture.arm_instruction import AReg
from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.corruption.corruptors import PacketCorruptor
from semantic_codec.metadata.collector import MetadataCollector, CorruptedProgramMetadataCollector
from semantic_codec.metadata.rules import from_instruction_list_to_dict


class TestMetadataCollector(TestCase):

    ASM_PATH = os.path.join(os.path.dirname(__file__), 'data/dissasembly.armasm')
    ASM_LONG_PATH = os.path.join(os.path.dirname(__file__), 'data/helloworld.armasm')

    def test_corrupted_collect(self):
        # TODO: This is an smoke test

        # Load the program
        instructions = TextDisassembleReader(self.ASM_LONG_PATH).read_instructions()

        # Corrupt the program
        ll = len(instructions)
        packet_count = ll / 32
        cc = PacketCorruptor(packet_count, ll, packets_lost=[3])
        instructions = cc.corrupt(from_instruction_list_to_dict(instructions))

        # Collect some metrics in the corrupted program
        c = CorruptedProgramMetadataCollector()
        c.collect(instructions)

        # Some very soft tests
        self.assertGreater(len(c.address_with_cond), 0)
        self.assertGreater(len(c.address_with_reg), 0)
        self.assertGreater(len(c.address_with_op), 0)

    def test_collect(self):
        instructions = TextDisassembleReader(self.ASM_PATH).read_instructions()
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