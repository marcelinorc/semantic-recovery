from pygraph.classes.digraph import digraph

from metadata.arm_instruction import AOpType
from metadata.bits import Bits


class ARMControlFlowGraphBuilder(object):
    """
    Computes the control flow graph of an ARM Instruction code segment
    """

    def __init__(self, instructions):
        self._instructions = instructions
        self._root_node = CFGBlock([], kind=CFGBlock.ROOT)
        self._cfg = None
        self._pending_jumps = {}

    @property
    def cfg(self):
        return self._cfg

    @property
    def root_node(self):
        return self._root_node

    def _add_node(self, n):
        """
        Convenience method
        """
        if not n in self._cfg:
            self._cfg.add_node(n)
        return n

    def _get_node_with_inst(self, instruction):
        """
        Get a node containing a certain instruction
        """
        # TODO: Replace with a bin search if needed for performance reasons
        for b in self._cfg:
            if instruction in b.instructions:
                return b
        return None

    def _find_instruction_by_address(self, instruction):
        """
        Returns the instruction located in a given address
        """
        # If a branch jumps to the content of a register there is little to do in static analysis,
        # the jump address is unknown. Also if the jumping instruction is beyond the address of the current
        # program, is also unknown
        # in_memory = self._instructions[0].position <= inst.jumping_address <= self._instructions[-1].position
        #  len(inst.registers_used()) > 0 or not in_memory
        pass

    def _split_node(self, split, branch, instruction):
        """
        Split a node that receives in the middle a jump from a jumping instruction
        """
        index = split.instructions.index(instruction)
        up = self._add_node(CFGBlock(split.instructions[:index]))
        split.instructions = split.instructions[index:]

        successors = []
        successors.extend(self._cfg.incidents(split))
        for i in successors:
            self._cfg.del_edge((i, split))
            self._cfg.add_edge((i, up))

        self._cfg.add_edge((up, split))
        self._cfg.add_edge((branch, split))

    def _branch_conditional(self, inst, cb, last_conditional):
        """
        Creates a branch in the CFG due to a change in the conditional field of the instruction
        """
        # Second case, the conditional field is different
        # Create a new block and add it to the graph
        b = self._add_node(CFGBlock(inst))
        r = self._cfg
        # Case 2.1 the new condition is not ALWAYS, therefore a new conditional node must be created
        if inst.conditional_field != (AOpType.ALWAYS >> 28):
            # Create the new conditional field
            new_cond = self._add_node(CFGBlock([], kind=CFGBlock.COND))
            # Add an outgoing edge to the new block from the conditional
            r.add_edge((new_cond, b))

            # if the last block is a branch, we cannot receive control from it
            # therefore only add and edge if is not a branch
            if not cb.last_is_branch:
                r.add_edge((cb, new_cond))

            # if a previous conditional existed, we must connect them both
            if last_conditional is not None and not r.has_edge((last_conditional, new_cond)):
                r.add_edge((last_conditional, new_cond))

            if inst in self._pending_jumps:
                self._add_multiple_edges(new_cond, self._pending_jumps[inst])

            # Make the las conditional seen this conditional node
            return b, new_cond
        else:
            # If the new conditional is ALWAYS, then, there is no need for a conditional node,
            # just jump to here, unless of course the previous node was a branch
            if not cb.last_is_branch:
                r.add_edge((cb, b))
            # Make the last conditional jump here
            if last_conditional is not None and not r.has_edge((last_conditional, b)):
                r.add_edge((last_conditional, b))

            # There no need for a last conditional node since the last block was not conditionally executed
            return b, None

    def _next_instruction(self, index):
        return self._instructions[index + 1] if len(self._instructions) - 2 > index else None

    def _add_pending_jump(self, instruction, block):
        """
        Add a block to the list of blocks jumping to a particular instruction
        """
        if instruction in self._pending_jumps:
            self._pending_jumps[instruction].append(block)
        else:
            self._pending_jumps[instruction] = [block]

    def _is_pointed_by_pending_jump(self, inst):
        pass

    def _branch_instruction(self, cb, branch, inst, end):
        """
        Creates a branch in the CFG due to a branching instruction
        """
        # ----------------------------
        # Third case, the BRANCHES
        # ----------------------------
        # Explicit branch i.e. because of a branch instruction
        r = self._cfg
        # Create the node with the explicit branch
        if branch is None:
            branch = self._add_node(CFGBlock([inst]))
        if cb is not None:
            r.add_edge((cb, branch))

        # Find the instruction where we are going to branch to
        # It may be None as is not possible to find out using an static analysis
        instruction_to_branch = inst.branch_to(self._instructions)
        if instruction_to_branch is None:
            unknown_node = self._add_node(CFGBlock([], kind=CFGBlock.UNKNOWN_BRANCH))
            r.add_edge((branch, unknown_node))
            r.add_edge((unknown_node, end))
            # A branch with link does jump to the next after returning from the call
            if inst.is_branch_with_link:
                cb = unknown_node
                #self._add_pending_jump(self._next_instruction(i), unknown_node)
        else:
            # 1 - Branch to the known address
            # if we branch with link we must put the next instruction in the pending jumps
            if inst.is_branch_with_link:
                raise RuntimeError("Not implemented yey")
                # cb = self._add_pending_jump(self._next_instruction(i), branch_node)

            # find out to what node the address jumps to
            to_node = self._get_node_with_inst(instruction_to_branch)
            if to_node is None:
                # the node is not built yet
                self._add_pending_jump(inst, branch)
            elif to_node.kind == CFGBlock.COND:
                # the node is a conditional
                self._cfg.add_edge(branch, to_node)
            else:
                # the node is a block of instructions
                self._split_node(to_node, branch, instruction_to_branch)

        return cb

    def _add_multiple_edges(self, dest, sources):
        """
        Build a edges going from all the nodes in "sources" to the "dest"
        """
        for s in sources:
            if not self._cfg.has_edge((s, dest)):
                self._cfg.add_edge((s, dest))

    def build(self, count=-1):
        """
        Computes the approximate CFG for a set of instructions

        When analysing a new instruction into the CFG graph 3 cases can happen:
        1 - The instruction DOES NOT have a different conditional than the previous one,
            hence it stays in the same block
        2 - The instruction DO have a different conditional than the previous one,
            2.1 If the new condition IS NOT ALWAYS, a conditional node is created to signal a bifurcation in the CFG
                and THEN a new block is created
            2.1 If the new conditional is ALWAYS a new block is created
        3 - The node is a branch, a new block is created only for the branch.
            3.1 - If the branch jumps to a known address, the Block containing the address is split in two,
                  and the second half receives the edge from the jump.

                  *** If the instruction is the first instruction of a conditional block,
                  the jump is received by the conditional

            3.2 - If the address is unknown, a new UNKNOWN block is created that is then connected to the END node
            3.3 - If the branch has link, then the UNKWNON node returns to the next created Node
        """
        count = len(self._instructions) if count == -1 else count

        # TODO: Missing the jumps due to MOVs writing to PC
        self._cfg = r = digraph()
        if len(self._instructions) == 0:
            return r

        # Addresses of the jumps ahead, last conditional found,
        last_cond_field = None
        # Last "conditional" node created and last "unknown" node created
        last_cond_node, unkwon_node = None, None
        # Add ROOT and END to the graph
        cb = self._add_node(self.root_node) # Make ROOT the current block
        end = self._add_node(CFGBlock([], kind=CFGBlock.END))

        for i in range(0, count):
            inst = self._instructions[i]
            if inst.conditional_field == last_cond_field:
                last_cond_field = inst.conditional_field
                # First case, just add the instruction to the current block
                # unless the current instruction is a branch:
                if inst.is_branch:
                    cb = self._branch_instruction(cb, None, inst, end)
                    last_cond_field = None
                elif inst in self._pending_jumps:
                    b = self._add_node(CFGBlock([inst]))
                    self._add_multiple_edges(b, self._pending_jumps[inst])
                    r.add_edge((cb, b))
                    cb = b
                else:
                    cb.instructions.append(inst)
            else:
                last_cond_field = inst.conditional_field
                # Second case, the conditional is different. Make the current node the last
                #  created node and the last conditional the current inst conditional
                cb, last_cond_node = self._branch_conditional(inst, cb, last_cond_node)
                if inst.is_branch:
                    self._branch_instruction(None, cb, inst, end)

        if not r.has_edge((cb, end)):
            r.add_edge((cb, end))
        return self._cfg



class CFGBlock(object):
    BLOCK = 0
    ROOT = 1
    COND = 2
    UNKNOWN_BRANCH = 3
    END = 4
    COND_IDX = 0
    UNKNOWN_BRANCH_IDX = 0

    _GLOBAL_IDX = 0

    def __init__(self, instructions, kind=BLOCK):

        CFGBlock._GLOBAL_IDX += 1
        self._globalid = CFGBlock._GLOBAL_IDX

        # Data for special kinds of nodes
        self._kind = kind
        if kind == CFGBlock.COND:
            CFGBlock.COND_IDX += 1
            #self._kind_idx = CFGBlock.COND_IDX
        elif kind == CFGBlock.UNKNOWN_BRANCH:
            CFGBlock.UNKNOWN_BRANCH_IDX += 1
            #self._kind_idx = CFGBlock.UNKNOWN_BRANCH_IDX

        self.branching_address = None

        # Instructions belonging to the node
        self.instructions = instructions if type(instructions) is list else [instructions]

        # Predecessors and successors in the CFG graph
        self.successors = []
        self.predecessors = []

        # The phi functions of this node. Each entry in the dictionary is a phi function where the
        # key is the variable being assigned and the elements in the list are the parameters of the function
        # i.e. phi_functions[key] <- phi( phi_functions[key][0], ... phi_functions[key][n])
        self.phi_functions = {}

        # Data relative to the Dominator tree
        self.dom_idx = -1
        # Parent in the DFS tree needed to find the dominator
        self.dom_parent = None
        self.dom_successors = []
        self.dom_semi = self
        # Immediate Dominator
        self.idom = None
        self.dom_ancestor = None
        self.dom_best = self
        self.dom_bucket = []
        self.dom_frontier = []

    @property
    def dom_semi_idx(self):
        k = self.dom_semi.dom_idx
        if k < 0:
            raise RuntimeError("Impossible!")
        return k

    def __str__(self):
        if self._kind == CFGBlock.ROOT:
            return "{}-ROOT".format(self._globalid)
        elif self._kind == CFGBlock.COND:
            return " <{}> ".format(self._globalid)
        elif self._kind == CFGBlock.UNKNOWN_BRANCH:
            return "{}-UNKWN".format(self._globalid)
        elif self._kind == CFGBlock.END:
            return "{}-END".format(self._globalid)
        if self.first == self.last:
            return "{}-{}".format(self._globalid, self.first)
        return "{}- {} ... {}".format(self._globalid, self.first, self.last)

    @property
    def kind(self):
        return self._kind

    @property
    def first_position(self):
        return 0 if self._kind else self.first.position

    @property
    def last_position(self):
        return 0 if self._kind else self.last.position

    @property
    def first(self):
        return self.instructions[0]

    @property
    def last(self):
        return self.instructions[-1]

    @property
    def last_is_branch(self):
        return False if len(self.instructions) == 0 else self.instructions[-1].is_branch

    @property
    def last_is_branch_with_link(self):
        """
        Indicates that the last instruction is a branch with link
        """
        return False if len(self.instructions) == 0 else self.instructions[-1].is_branch_with_link


class SSAFormBuilder(object):
    """
    Computes the approximate value dependency graph in ssa form
    """

    def __init__(self, instructions, graph, root):
        self._graph = graph
        self._root = root
        self._instructions = instructions

    def build(self):
        # Compute the Dominators tree
        DominatorTreeBuilder(self._graph, self._root).build()
        # Compute dominance frontiers
        self._dominance_frontiers()

        # Find global names tpo minimize phi function emplacement
        global_vars = self._place_phi_nodes()

        self._rename_vars(global_vars)

        d = digraph()
        for inst in self._instructions:
            for r in inst.ssa_written:
                if r not in d:
                    d.add_node(d)
                for w in inst.ssa_read:
                    if w not in d:
                        d.add_node(w)
                    if not d.has_edge((r, w)):
                        d.add_edge((r, w))
        return d

    def _place_phi_nodes(self):
        # Find those variables that are used in more than one block
        blocks = {}
        globals_vars = []
        for node in self._graph:
            var_kill = []
            for inst in node.instructions:
                read = inst.registers_read()
                written = inst.registers_written()

                for r in read:
                    if r not in globals_vars and r not in var_kill:
                        globals_vars.append(r)
                for w in written:
                    if w not in var_kill:
                        var_kill.append(w)
                    if w in blocks:
                        if node not in blocks[w]:
                            blocks[w].append(node)
                    else:
                        blocks[w] = [node]

        # place the nodes
        for x in globals_vars:
            if x in blocks:
                work_list = blocks[x]
                i = 0
                while i < len(work_list):
                    b = work_list[i]
                    for d in b.dom_frontier:
                        if x not in d.phi_functions:
                            d.phi_functions[x] = []
                            if d not in work_list:
                                work_list.append(d)
                    i += 1

        return globals_vars

    def _dominance_frontiers(self):
        """
        Finds the dominance frontiers for an smart phi function placement in the SSA form
        """
        for n in self._graph:
            if len(n.predecessors) > 0:
                for p in n.predecessors:
                    runner = p
                    while runner != n.idom:
                        runner.dom_frontier.append(n)
                        runner = runner.idom

    @staticmethod
    def _new_name(n, counter, stack):
        """
        Increases the counter for a given variable
        """
        i = counter[n]
        stack[n].insert(0, i)
        counter[n] += 1
        return n, i

    def _rename_vars(self, global_vars):
        """
        Rename the variables in the SSA
        """
        counter = {}
        stack = {}
        for v in range(0, 16):
            counter[v] = 0
            stack[v] = [0]

        self._rename_node(self._root, counter, stack)

    def _rename_node(self, n, counter, stack):
        """
        Rename the variables in SSA form in the nodes of the CFG
        """
        keys = n.phi_functions.keys()
        for phi in keys:
            # Get the new name for the variable
            x = self._new_name(phi, counter, stack)
            # Replace the phi function using the new name
            n.phi_functions[x] = n.phi_functions[phi]
            del n.phi_functions[phi]

            # Fill the parameters of successors phi functions
            for b in n.successors:
                if phi in b.phi_functions:
                    b.phi_functions[phi].append(x)

        # Rename all variables in the block
        for inst in n.instructions:
            for r in inst.registers_read():
                if (r, stack[r]) not in inst.ssa_read:
                    inst.ssa_read.append((r, stack[r][0]))
            for w in inst.registers_written():
                new_w = self._new_name(w, counter, stack)
                inst.ssa_written.append((w, new_w))

        # Continue the renaming process in the successors
        for n in n.dom_successors:
            self._rename_node(n, counter, stack)

        # Roll back the indexing
        for phi in n.phi_functions:
            for inst in n.instructions:
                if phi in inst.registers_written:
                    stack[phi].pop()
            stack[phi].pop()


class ValueDependenceTreeBuilder(object):
    """
    Builds the value dependence tree(s)
    """

    def build(self):
        pass


class DominatorTreeBuilder(object):
    """
    Builds the dominator tree
    """

    def __init__(self, digraph, root):
        """
        Receives the graph for which the dominator tree is going to be built
        """
        self._graph = digraph
        self._root = root

    def _dfs(self, node, visited, index=0):
        result = [node]
        node.dom_idx = index
        node.predecessors = self._graph.incidents(node)
        node.successors = self._graph.neighbors(node)
        visited.append(node)
        for n in node.successors:
            if n not in visited:
                n.dom_parent = node
                result.extend(self._dfs(n, visited, index + 1))

        return result

    def build(self):
        # Initialization
        vertex = self._dfs(self._root, [])

        for i in range(len(vertex) - 1, 0, -1):
            w = vertex[i]
            p = w.dom_parent
            for v in w.predecessors:
                u = self._eval(v)
                if u.dom_semi_idx < w.dom_semi_idx:
                    w.dom_semi = u.dom_semi

            #vertex[w.dom_semi_idx].dom_bucket.append(w)
            w.dom_semi.dom_bucket.append(w)
            # LINK:
            w.dom_ancestor = p

            while len(p.dom_bucket) > 0:
                v = p.dom_bucket.pop()
                u = self._eval(v)
                v.idom = u if u.dom_semi_idx < v.dom_semi_idx else w.dom_parent

        for i in range(1, len(vertex)):
            w = vertex[i]
            if w.idom != w.dom_semi:
                w.idom = w.idom.idom

        vertex[0].idom = None

        tree = digraph()
        for n in self._graph:
            tree.add_node(n)
        for n in self._graph:
            if n.idom is not None:
                if not n in n.idom.dom_successors:
                    n.idom.dom_successors.append(n)
                if not tree.has_edge((n.idom, n)):
                    tree.add_edge((n.idom, n))
        return tree

    def _eval(self, v):
        a = v.dom_ancestor
        if a is None:
            return v
        while a.dom_ancestor is not None:
            if v.dom_semi_idx > a.dom_semi_idx:
                v = a
            a = a.dom_ancestor
        return v
