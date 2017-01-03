import os
from unittest import TestCase
from pygraph.classes.digraph import digraph

from dot.dotio import write
from metadata.analysis import ARMControlFlowGraphBuilder, DominatorTreeBuilder, SSAFormBuilder
from metadata.disassembler_readers import TextDisassembleReader


class TestValueDependencySSABuilder(TestCase):

    def test_build(self):

        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'dissasembly.armasm')).read()
        graph_builder = ARMControlFlowGraphBuilder(instructions)
        graph_builder.build()
        dom_tree = DominatorTreeBuilder(graph_builder.cfg, graph_builder.root_node).build()
        self.assertTrue(7 < len(dom_tree.edges()))
        self.assertTrue(8 < len(dom_tree.nodes()))

        value_dep_graph = SSAFormBuilder(instructions, graph_builder.cfg, graph_builder.root_node).build()
        self.assertTrue(value_dep_graph is not None)

        print(write(value_dep_graph))


