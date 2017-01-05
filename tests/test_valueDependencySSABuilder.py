import os
from unittest import TestCase

from dot.dotio import write
from metadata.disassembler_readers import TextDisassembleReader
from metadata.static_analysis.cfg import ARMControlFlowGraph
from metadata.static_analysis.dominators import build_dominator_tree
from metadata.static_analysis.ssa import SSAFormBuilder, build_dominance_frontier


class TestValueDependencySSABuilder(TestCase):

    def _build_cfg_with_dominators(self, path):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), path)).read()
        cfg = ARMControlFlowGraph(instructions)
        cfg.build()
        build_dominator_tree(cfg, cfg.root_node)
        return cfg, instructions

    def test_dominance_frontier(self):
        graph, instructions = self._build_cfg_with_dominators('dissasembly.armasm')
        build_dominance_frontier(graph)
        for n in graph:
            print('{} - {}'.format(n, n.dom_frontier))

    def test_build(self):
        graph, instructions = self._build_cfg_with_dominators('dissasembly.armasm')
        value_dep_graph = SSAFormBuilder(instructions, graph, graph.root_node).build()
        self.assertTrue(value_dep_graph is not None)
        print(write(value_dep_graph))


