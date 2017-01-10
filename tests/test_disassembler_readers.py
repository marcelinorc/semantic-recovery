import os
import unittest

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader

class TestTextDisassembleReader(unittest.TestCase):

    ASM_PATH = os.path.join(os.path.dirname(__file__), 'data/dissasembly.armasm')
    HELLO_PATH = os.path.join(os.path.dirname(__file__), 'data/helloworld.armasm')

    def test_read(self):
        instructions = TextDisassembleReader(self.ASM_PATH).read()
        self.assertEqual(24, len(instructions))
        self.assertEqual(0x00010790, instructions[0].position)
        self.assertEqual(0x000107ec, instructions[len(instructions) - 1].position)

    def test_read_hello_world(self):
        instructions = TextDisassembleReader(self.HELLO_PATH).read()
        self.assertEqual(177, len(instructions))
        for inst in instructions:
            print(inst)
            if not str(inst.darm):
                print("Jony, la gente esta muy loka")
            if inst.is_undefined:
                print('Undefined')

    def test_read_functions(self):
        fns = TextDisassembleReader(self.HELLO_PATH).read_functions()
        self.assertEqual(35, len(fns))
        self.assertEqual(11, len(fns['.text:000106d0 <frame_dummy>:']))
        self.assertEqual(9, len(fns['.text:000106a8 <__do_global_dtors_aux>:']))

