import os
from unittest import TestCase
from architecture.disassembler_readers import TextDisassembleReader
from dot.dotio import write
from static_analysis.cfg import ARMControlFlowGraph
from static_analysis.dominators import build_dominator_tree


class TestDominatorTreeBuilder(TestCase):


    def test_build(self):
        """
        Build the dominator tree
        """
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'dissasembly.armasm')).read()
        graph_builder = ARMControlFlowGraph(instructions)
        graph_builder.build()
        dom_tree = build_dominator_tree(graph_builder.cfg, graph_builder.root_node)
        self.assertTrue(7 < len(dom_tree.edges()))
        self.assertTrue(8 < len(dom_tree.nodes()))
        print(write(dom_tree))

