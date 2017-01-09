import os
import unittest

from architecture.disassembler_readers import TextDisassembleReader


class TestTextDisassembleReader(unittest.TestCase):

    def test_read(self):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'dissasembly.armasm')).read()
        self.assertEqual(24, len(instructions))
        self.assertEqual(0x00010790, instructions[0].position)
        self.assertEqual(0x000107ec, instructions[len(instructions) - 1].position)

    def test_read_hello_world(self):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'helloworld.armasm')).read()
        self.assertEqual(177, len(instructions))
        for inst in instructions:
            print(inst)
            if not str(inst.darm):
                print("Jony, la gente esta muy loka")
            if inst.is_undefined:
                print('Undefined')
