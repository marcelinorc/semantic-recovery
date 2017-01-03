import os
from unittest import TestCase

from metadata.collector import MetadataCollector
from metadata.disassembler_readers import TextDisassembleReader


class TestMetadataCollector(TestCase):

    def test_collect(self):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'dissasembly.armasm')).read()
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
