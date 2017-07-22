import sys
from math import log

from semantic_codec.metadata.recuperator import probabilistic_rules


class AnswerQuality(object):
    """
    Class that computes the Answer's quality so far
    """

    def __init__(self, program, original_program):
        # The highest depth in the solution (i.e. the worst place a correct answer has)
        self._highest_depth = None

        # Compute the number of possible solutions
        self._solution_count = -1

        # Amount of addresses with 2, 4, 8, 16, 32... candiates
        self._solution_count_bins = None

        self._program = program

        self._original_program = original_program

    @property
    def highest_depth(self):
        if self._highest_depth is None:
            self.evaluate()
        return self._highest_depth

    @property
    def solution_count_bins(self):
        if not self._solution_count_bins:
            self._count_solutions(self._program)
        return self._solution_count_bins

    @property
    def solution_count(self):
        if self._solution_count == -1:
            self._count_solutions(self._program)
        return self._solution_count

    def _count_solutions(self, program):
        bins = {}
        max_v = 0
        for v in program.values():
            k = len(v)
            if k > max_v:
                max_v = k
            if k in bins:
                bins[k] += 1
            else:
                bins[k] = 1

        i = 1
        amount = sys.maxsize
        result = 0
        can_represent = True
        for i in bins.keys():
            if not can_represent or amount < 0:
                break
            if i > 1:
                k = log(amount, i)
                if k > bins[i]:
                    result += i ** bins[i]
                    amount -= result
                else:
                    can_represent = False
            elif i != 0:
                amount -= 1
                result += 1

        if can_represent:
            self._solution_count = result
        else:
            self._solution_count = None
        self._solution_count_bins = bins

    def evaluate(self):
        self._solution_count = self._count_solutions(self._program)

        # Change the probabilistic function to one more continous

        for k in range(0, len(self._original_program)):
            v = self._program[self._original_program[k].position]
            for inst in v:
                inst.score_function = probabilistic_rules
            v.sort(key=lambda x : x.score())

            i = 0
            while i < len(v) and i < self._solution_count_bins[k] and v[i] != self._original_program[i]:
                i += 1

            if i > self._highest_depth:
                self._highest_depth = i