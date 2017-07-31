from math import log

from constraint import *

from semantic_codec.architecture.bits import BitQueue
from semantic_codec.metadata.collector import MetadataCollector
from semantic_codec.metadata.rules import from_instruction_list_to_dict


class ExactFieldSumConstraint(Constraint):
    """
    Constraint enforcing that values of given variables sum exactly
    to a given amount
    Example:
    >>> problem = Problem()
    >>> problem.addVariables(["a", "b"], [1, 2])
    >>> problem.addConstraint(ExactFieldSumConstraint(3))
    >>> sorted(sorted(x.items()) for x in problem.getSolutions())
    [[('a', 1), ('b', 2)], [('a', 2), ('b', 1)]]
    """

    def __init__(self, exactsum, field_fn, report=False):
        self._exactsum = exactsum
        self._field_fn = field_fn
        self._report = report

    def __call__(self, variables, domains, assignments, forwardcheck=False):

        exactsum = self._exactsum

        sum = {}
        for k in exactsum:
            sum[k] = 0

        missing = False
        for variable in variables:
            if variable in assignments:
                inst = assignments[variable]
                if inst.ignore:
                    continue
                vv = self._field_fn(inst)
                for v in vv:
                    if not v in sum:
                        sum[v] = 1
                    else:
                        sum[v] += 1
            else:
                missing = True

        for k in sum:
            if not k in exactsum or sum[k] > exactsum[k]:
                return False

        if forwardcheck and missing:
            for variable in variables:
                if variable not in assignments:
                    domain = domains[variable]
                    for value in domain[:]:
                        if value and not value.ignore:
                            vv = self._field_fn(value)
                            for v in vv:
                                if not v in exactsum or sum[v] + 1 > exactsum[v]:
                                    domain.hideValue(value)
                    if not domain:
                        return False
        if missing:
            for k in sum:
                if sum[k] > exactsum[k]:
                    return False
        else:
            for k in sum:
                if sum[k] != exactsum[k]:
                    return False
        return True


class ProblemBuilder(object):
    def build(self, program, metadata):
        problem = Problem()
        for k, v in program.items():
            if len(v) > 0:
                problem.addVariable(k, [x for x in v])
        problem.addConstraint(ExactFieldSumConstraint(metadata.condition_count, lambda x: [x.conditional_field]))
        problem.addConstraint(ExactFieldSumConstraint(metadata.instruction_count, lambda x: [x.opcode_field]))
        problem.addConstraint(ExactFieldSumConstraint(metadata.storage_count, lambda x: x.storages_used()))
        problem.getSolver()
        # problem.addConstraint(ExactRegisterSumConstraint(metadata.conditional_count))
        # problem.addConstraint(ExactOpcodeSumConstraint(metadata.conditional_count))
        return problem


class ForwardConstraintRecuperator(object):
    """
    This class takes a solution built by the solution builder and then
    """
    pass


class ForwardConstraintSolutionWorker(object):

    def __init__(self, program, original_program):
        self._from_max_to_min = False
        self._program = program
        self._metadata = MetadataCollector()
        self._metadata.collect(original_program)
        self._solution_size = 0
        self._original = from_instruction_list_to_dict(original_program)
        self._solution = BitQueue()
        self._forward_update = False
        # Indicates min number of candidates an address is reduced to
        self._candidates_reduced = None

    @property
    def solution(self):
        return self._solution

    @property
    def solution_size(self):
        return self._solution_size

    def _comply_constraints(self, inst):
        """
        Indicates if selecting an instruction as solution
        :param inst:
        :return:
        """
        if inst.ignore:
            return False

        m = self._metadata
        if not inst.opcode_field in m.instruction_count or m.instruction_count[inst.opcode_field] == 0:
            return False

        if not inst.conditional_field in m.condition_count or m.condition_count[inst.conditional_field] == 0:
            return False

        for r in inst.registers_used():
            if not r in m.storage_count or m.storage_count[r] == 0:
                return False

        return True

    def _remove_invalid_instructions(self, addresses):
        """
        Remove all instructions not complaining with current constraints
        :return: True if some instructions were removed
        """
        for k in range(1, len(addresses)):
            a = addresses[k]
            i = 1
            pa = self._program[a]
            while i < len(pa):
                if not self._comply_constraints(pa[i - 1]):
                    pa.pop(i - 1)
                else:
                    i += 1

    def _update_constraints(self, inst):
        if inst.opcode_field in self._metadata.instruction_count:
            self._metadata.instruction_count[inst.opcode_field] -= 1

        if inst.conditional_field in self._metadata.condition_count:
            self._metadata.condition_count[inst.conditional_field] -= 1

        for r in inst.storages_used():
            if r in self._metadata.storage_count:
                self._metadata.storage_count[r] -= 1

    def _find_address_correct_index(self, pa, ori, ln):
        index = 0
        while index < ln and str(pa[index]) != str(ori):
            index += 1
        if index == ln:
            raise RuntimeError('Impossible')
        return index

    def build(self):
        addresses = [x for x in self._program.keys()]
        addresses.sort(key=lambda x: len(self._program[x]), reverse=self._from_max_to_min)

        while len(addresses) > 0:
            pa = self._program[addresses[0]]
            ln = len(pa)
            ori = self._original[addresses[0]][0]
            if ln <= 0 or ori.ignore:
                addresses.pop(0)
                continue

            index = 0
            if ln > 1:
                index = self._find_address_correct_index(pa, ori, ln)
                self._on_index_found(index, pa, ori, ln)

            if self._forward_update:
                # Update the constrains now that we have updated the solution
                self._update_constraints(pa[index])
                # With the constrains updated, remove all instructions which are invalid
                self._remove_invalid_instructions(addresses)

            addresses.pop(0)
            # if self._candidates_reduced:
            addresses.sort(key=lambda x: len(self._program[x]), reverse=self._from_max_to_min)



    def _on_index_found(self, size, pa, ori, ln):
        pass


class ForwardConstraintSolutionEnumerator(ForwardConstraintSolutionWorker):
    """
    Enumerates all possible solutions and returns the index of the correct. Is a forward constraint because
    it deletes candidates as it progresses.
    """
    def __init__(self, program, original_program):
        super(self.__class__, self).__init__(program, original_program)
        self._from_max_to_min = False
        self._forward_update = True
        self._solution = 1

    def _on_index_found(self, index, size, pa, ori):
        # Compute the size of the solution
        if index < 0:
            raise RuntimeError('Impossible')

        self._solution *= (index + 1)
        self._solution_size = log(self._solution, 2)




class ForwardConstraintSolutionBuilder(ForwardConstraintSolutionWorker):
    """
    This class builds a solution in the following way:
    1. It sorts the addresses by the number of candidates.
    2. To the addresses with less candidates, it gives a number to each addresses indicating the address solution.
    3. Updates the number of candidates in the other addresses, removing all candidates that does not comply to constrainst
    4. Goes to 1 until all addresses solutions are known
    """

    def _on_index_found(self, index, cand_list, ori, ln):
        """
        Event called when the solution is found in an address
        :param index: Index found
        :param cand_list: List of candidates in the address
        :param ori: Original instruction in the address
        :param ln: Amount of candidates in the address
        :return:
        """
        if index is not None:
            size = int(log(ln, 2)) if ln > 1 else 0
            # Compute the size of the solution
            self._solution_size += size
            # Enqueue some bits to the solution
            index = self._find_address_correct_index(cand_list, ori, ln)
            self._solution.word_size = size
            self._solution.enqueue(index, 0)


