import os
import unittest
from unittest import TestCase

from pygraph.classes import digraph

from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.static_analysis.cfg import ARMControlFlowGraph
from semantic_codec.static_analysis.dominators import build_dominator_tree
from semantic_codec.static_analysis.ssa import SSAFormBuilder, build_dominance_frontier, place_phi_nodes

from libs.dot.dotio import write


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

    def _is_connected_graph(self, graph, root, visited=None):
        """
        Checks that the graph is connected
        """
        if not visited:
            visited = []
        for n in graph.neighbors(root):
            if not n in visited:
                visited.append(n)
                self._is_connected_graph(graph, n, visited)
        for n in graph.incidents(root):
            if not n in visited:
                visited.append(n)
                self._is_connected_graph(graph, n, visited)

        return len(visited) == len(graph)

    def _build_cfg_with_dominators(self, path, printer=None, remove_conditionals=False):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), path)).read_instructions()
        cfg = ARMControlFlowGraph(instructions)
        cfg.node_printer = printer
        cfg.build()
        if remove_conditionals:
            cfg.remove_conditionals()
        build_dominator_tree(cfg, cfg.root_node)
        return cfg, instructions

    def test_dominance_frontier(self):
        graph, instructions = self._build_cfg_with_dominators('data/dissasembly.armasm')
        build_dominance_frontier(graph)
        print(write(graph))
        d = graph.get_dict_nodes()
        for n in graph:
            print('<< {} >> - {}'.format(n, n.dom_frontier))
        # The root as no frontier
        self.assertEqual(0, len(d[1].dom_frontier))
        # A random node's frontier pick to evaluate
        self.assertTrue(d[2] in d[15].dom_frontier)
        self.assertTrue(d[10] in d[15].dom_frontier)
        # A node who's frontier contains himself
        self.assertTrue(d[10] in d[10].dom_frontier)

    def test_phi_node_placement(self):
        graph, instructions = self._build_cfg_with_dominators('data/dissasembly.armasm', self, remove_conditionals=True)
        build_dominance_frontier(graph)
        place_phi_nodes(graph)

        d = graph.get_dict_nodes()
        # Nodes with phi functions
        self.assertTrue(len(d[10].phi_functions) > 0)
#        self.assertTrue(len(d[2].phi_functions) > 0)
        # Nodes without phi functions
        self.assertTrue(len(d[4].phi_functions) == 0)
        self.assertTrue(len(d[6].phi_functions) == 0)
        self.assertTrue(len(d[12].phi_functions) == 0)

        print(write(graph))

    def _build_ssa(self, path):
        instructions = TextDisassembleReader(os.path.join(os.path.dirname(__file__), path)).read_instructions()
        cfg = ARMControlFlowGraph(instructions)
        cfg.node_printer = self
        cfg.build()
        d = cfg.get_dict_nodes()
        cfg.remove_conditionals()
        value_dep_graph = SSAFormBuilder(instructions, cfg, cfg.root_node).build()
        return cfg, value_dep_graph

    def test_build(self):
        cfg, value_dep_graph = self._build_ssa('data/dissasembly.armasm')
        print(write(cfg))
        print(write(value_dep_graph))
        self.assertTrue(value_dep_graph is not None)

    @unittest.skip("This functionality is not used anymore")
    def test_build_simpler_code(self):
        cfg, value_dep_graph = self._build_ssa('data/simple.armasm')
        print(write(cfg))
        print(write(value_dep_graph))
        self.assertTrue(self._is_connected_graph(value_dep_graph, value_dep_graph.nodes()[0]))


