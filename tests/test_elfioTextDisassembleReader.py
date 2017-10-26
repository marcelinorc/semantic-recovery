from unittest import TestCase

from semantic_codec.architecture.disassembler_readers import ElfioTextDisassembleReader


class TestElfioTextDisassembleReader(TestCase):

    def test_read(self):
        fns, instructions = ElfioTextDisassembleReader("data/helloworld_elfiodissasembly.disam").read()
        # Some smoke to start with
        for inst in instructions:
            self.assertFalse(inst.ignore)
        self.assertEqual(instructions[0].encoding, 0xe92d4008)  # push {r3, lr}
        self.assertEqual(instructions[2].encoding, 0xe52de004)  # str lr, [sp, #-4]!
        self.assertEqual(instructions[len(instructions) - 2].encoding, 0xe8bd8800)  # pop {fp, pc}
        self.assertEqual(instructions[len(instructions) - 1].encoding, 0xe92d4008)  # push {r3, lr}
        self.assertGreater(len(fns), 10)
        self.assertEqual(len(instructions), 143)

