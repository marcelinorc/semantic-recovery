import os
from unittest import TestCase

from architecture.disassembler_readers import TextDisassembleReader
from dot.dotio import write
from static_analysis.cfg import ARMControlFlowGraph
from static_analysis.ssa import SSAFormBuilder, build_dominance_frontier, place_phi_nodes
from static_analysis.dominators import build_dominator_tree


class TestValueDependencySSABuilder(TestCase):

    def print(self, node):
        result = ""
        for phi, val in node.phi_functions.items():
            result += "{} = p({}) \n ".format(phi, val)
        for inst in node.instructions:
            result += "{} -- {} == {} \n ".format(inst, inst.ssa_written, inst.ssa_read)


        if not result:
            node.printer = None
            result += str(node)
            node.printer = self
        else:
            result += "{}".format(node.idx)
        return result

    def _build_cfg_with_dominators(self, path, printer=None, remove_conditionals=False):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), path)).read()
        cfg = ARMControlFlowGraph(instructions)
        cfg.node_printer = printer
        cfg.build()
        if remove_conditionals:
            cfg.remove_conditionals()
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
        graph, instructions = self._build_cfg_with_dominators('dissasembly.armasm', self, remove_conditionals=True)
        build_dominance_frontier(graph)
        place_phi_nodes(graph)

        d = graph.get_dict_nodes()
        # Nodes with phi functions
        self.assertTrue(len(d[15].phi_functions) > 0)
        self.assertTrue(len(d[9].phi_functions) > 0)
#        self.assertTrue(len(d[2].phi_functions) > 0)
        # Nodes without phi functions
        self.assertTrue(len(d[4].phi_functions) == 0)
        self.assertTrue(len(d[6].phi_functions) == 0)
        self.assertTrue(len(d[12].phi_functions) == 0)

        print(write(graph))

    def test_build(self):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), 'dissasembly.armasm')).read()
        cfg = ARMControlFlowGraph(instructions)
        cfg.node_printer = self
        cfg.build()
        d = cfg.get_dict_nodes()
        cfg.remove_conditionals()
        value_dep_graph = SSAFormBuilder(instructions, cfg, cfg.root_node).build()
        print(write(cfg))

        # Check that there are no dead phi nodes
#        self.assertTrue(SSAVar(3, 3) not in )
        print(write(value_dep_graph))
        self.assertTrue(value_dep_graph is not None)
        self.fail("Not sure...")


