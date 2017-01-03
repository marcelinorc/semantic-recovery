import os
from unittest import TestCase
from metadata.analysis import ARMControlFlowGraphBuilder, CFGBlock
from metadata.disassembler_readers import TextDisassembleReader
from dot.dotio import write


class TestARMControlFlowGraphBuilder(TestCase):

    @staticmethod
    def _count_conditional_nodes(cfg):
        result = 0
        for n in cfg.nodes():
            if n.kind == CFGBlock.COND:
                result += 1
        return result

    def _assert_instructions_are_not_repeated(self, graph, instructions):
        for i in instructions:
            k = 0;
            for b in graph:
                if b.kind != CFGBlock.COND and i in b.instructions:
                    k += 1
                    if k > 1:
                        self.fail("Instructions repeated")

    def test_build_simple(self):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'dissasembly.armasm')).read()
        builder = ARMControlFlowGraphBuilder(instructions)
        cfg = builder.build()

        print(write(cfg))
        self.assertTrue(18 < len(cfg.edges()))
        self.assertTrue(15 < len(cfg.nodes()))
        self.assertEqual(2, self._count_conditional_nodes(cfg))

        # This one is to catch a bug
        self.assertEqual(0, len(builder.root_node.instructions))

        self._assert_instructions_are_not_repeated(cfg, instructions)

    def test_build_complex(self):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'dissasembly_cfg.armasm')).read()
        cfg = ARMControlFlowGraphBuilder(instructions).build()
        print(write(cfg))
        self.assertTrue(10 < len(cfg.edges()))
        self.assertTrue(9 < len(cfg.nodes()))
        self.assertEqual(3, self._count_conditional_nodes(cfg))

        self._assert_instructions_are_not_repeated(cfg, instructions)



