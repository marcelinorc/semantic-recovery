import os
from unittest import TestCase

from dot.dotio import write
from metadata.disassembler_readers import TextDisassembleReader
from metadata.static_analysis.analysis import ARMControlFlowGraphBuilder, DominatorTreeBuilder


class TestDominatorTreeBuilder(TestCase):


    def test_build(self):
        """
        Build the dominator tree
        """
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'dissasembly.armasm')).read()
        graph_builder = ARMControlFlowGraphBuilder(instructions)
        graph_builder.build()
        dom_tree = DominatorTreeBuilder(graph_builder.cfg, graph_builder.root_node).build()
        self.assertTrue(7 < len(dom_tree.edges()))
        self.assertTrue(8 < len(dom_tree.nodes()))

        print(write(dom_tree))


