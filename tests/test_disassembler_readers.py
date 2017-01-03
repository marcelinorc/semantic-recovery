import os
import unittest
from metadata.disassembler_readers import TextDisassembleReader


class TestTextDisassembleReader(unittest.TestCase):

    def test_read(self):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'dissasembly.armasm')).read()
        self.assertEqual(24, len(instructions))
        self.assertEqual(0x00010790, instructions[0].position)
        self.assertEqual(0x000107ec, instructions[len(instructions) - 1].position)
