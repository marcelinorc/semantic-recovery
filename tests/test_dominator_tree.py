import os
from unittest import TestCase

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.static_analysis.cfg import ARMControlFlowGraph
from semantic_codec.static_analysis.dominators import build_dominator_tree

from libs.dot.dotio import write


class TestDominatorTreeBuilder(TestCase):

    ASM_PATH = os.path.join(os.path.dirname(__file__), 'data/dissasembly.armasm')

    def test_build(self):
        """
        Build the dominator tree
        """
        instructions = TextDisassembleReader(self.ASM_PATH).read_instructions()
        graph_builder = ARMControlFlowGraph(instructions)
        graph_builder.build()
        dom_tree = build_dominator_tree(graph_builder.cfg, graph_builder.root_node)
        self.assertTrue(7 < len(dom_tree.edges()))
        self.assertTrue(8 < len(dom_tree.nodes()))
        print(write(dom_tree))


