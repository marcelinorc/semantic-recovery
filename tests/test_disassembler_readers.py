import os
import unittest

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader

class TestTextDisassembleReader(unittest.TestCase):

    ASM_PATH = os.path.join(os.path.dirname(__file__), 'data/dissasembly.armasm')
    HELLO_PATH = os.path.join(os.path.dirname(__file__), 'data/helloworld.armasm')

    def test_read(self):
        instructions = TextDisassembleReader(self.ASM_PATH).read_instructions()
        self.assertEqual(24, len(instructions))
        self.assertTrue('push' in str(instructions[0]))
        self.assertTrue('mov' in str(instructions[1]))
        self.assertEqual(0x00010790, instructions[0].address)
        self.assertEqual(0x000107ec, instructions[len(instructions) - 1].address)

    def test_read_hello_world(self):
        instructions = TextDisassembleReader(self.HELLO_PATH).read_instructions()
        self.assertEqual(177, len(instructions))
        self.assertTrue('push' in str(instructions[0]))
        self.assertTrue('bl' in str(instructions[1]))
        #for inst in instructions:
        #    self.assertFalse(inst.is_undefined)

    def test_read_functions(self):
        fns = TextDisassembleReader(self.HELLO_PATH).read_functions()
        self.assertEqual(36, len(fns))
        self.assertEqual(11, len(fns[23].instructions))
        self.assertEqual(9, len(fns[21].instructions))

