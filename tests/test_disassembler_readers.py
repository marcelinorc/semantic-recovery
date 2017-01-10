import os
import unittest

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from tests.test_ARMControlFlowGraph import TestARMControlFlowGraph


class TestTextDisassembleReader(unittest.TestCase):

    def test_read(self):
        instructions = TextDisassembleReader(TestARMControlFlowGraph.ASM_PATH).read()
        self.assertEqual(24, len(instructions))
        self.assertEqual(0x00010790, instructions[0].position)
        self.assertEqual(0x000107ec, instructions[len(instructions) - 1].position)

    def test_read_hello_world(self):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'data/helloworld.armasm')).read()
        self.assertEqual(177, len(instructions))
        for inst in instructions:
            print(inst)
            if not str(inst.darm):
                print("Jony, la gente esta muy loka")
            if inst.is_undefined:
                print('Undefined')

    def test_read_functions(self):
        fns = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'data/helloworld.armasm')).read_functions()
        self.assertEqual(35, len(fns))
        self.assertEqual(11, len(fns['.text:000106d0 <frame_dummy>:']))
        self.assertEqual(9, len(fns['.text:000106a8 <__do_global_dtors_aux>:']))

