import os
from unittest import TestCase

from dot.dotio import write
from metadata.disassembler_readers import TextDisassembleReader
from metadata.static_analysis.cfg import ARMControlFlowGraph
from metadata.static_analysis.dominators import build_dominator_tree
from metadata.static_analysis.ssa import SSAFormBuilder, build_dominance_frontier, place_phi_nodes


class TestValueDependencySSABuilder(TestCase):

    def print(self, node):
        result = ""
        for phi in node.phi_functions:
            if len(node.phi_functions[phi]) > 0:
                result += "{} = p({}) \n ".format(phi[0], node.phi_functions[phi])
        node.printer = None
        result += str(node)
        node.printer = self
        return result

    def _build_cfg_with_dominators(self, path, printer=None):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), path)).read()
        cfg = ARMControlFlowGraph(instructions)
        cfg.node_printer = printer
        cfg.build()
        build_dominator_tree(cfg, cfg.root_node)
        return cfg, instructions

    def test_dominance_frontier(self):
        graph, instructions = self._build_cfg_with_dominators('dissasembly.armasm')
        build_dominance_frontier(graph)

        d = graph.get_dict_nodes()
        # for n in graph:
        #    print('<< {} >> - {}'.format(n, n.dom_frontier))
        # The root as no frontier
        self.assertEqual(0, len(d[1].dom_frontier))
        # A random node's frontier pick to evaluate
        self.assertTrue(d[2] in d[14].dom_frontier)
        self.assertTrue(d[9] in d[14].dom_frontier)
        # A node who's frontier contains himself
        self.assertTrue(d[9] in d[9].dom_frontier)

    def test_phi_node_placement(self):
        graph, instructions = self._build_cfg_with_dominators('dissasembly.armasm', self)
        build_dominance_frontier(graph)
        place_phi_nodes(graph)
        print(write(graph))

    def test_build(self):
        graph, instructions = self._build_cfg_with_dominators('dissasembly.armasm')
        value_dep_graph = SSAFormBuilder(instructions, graph, graph.root_node).build()
        self.assertTrue(value_dep_graph is not None)


