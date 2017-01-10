import os
from unittest import TestCase

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.metadata.collector import MetadataCollector


class TestMetadataCollector(TestCase):

    ASM_PATH = os.path.join(os.path.dirname(__file__), 'data/dissasembly.armasm')

    def test_collect(self):
        instructions = TextDisassembleReader(self.ASM_PATH).read()
        # Collect the metadata
        collector = MetadataCollector()
        collector.collect(instructions)

        self.assertEqual(3, len(collector.condition_count))

        prev_inst = None
        for inst in collector.empty_spaces:
            if prev_inst is None:
                print('{}; 0; {}'.format(inst.encoding, inst))
            else:
                print('{}; {}; {}'.format(inst.encoding, abs(prev_inst.encoding - inst.encoding), inst))
            prev_inst = inst
