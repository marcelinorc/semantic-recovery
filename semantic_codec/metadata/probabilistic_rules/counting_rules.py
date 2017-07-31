import copy

from semantic_codec.metadata.probabilistic_rules.rules import Rule


class CountingRule(Rule):

    def __init__(self, program, model=None, collector=None):
        super().__init__(program, model)
        if collector is None:
            raise RuntimeError("Needs a metadata collector")
        self._collector = collector
        self._scores = {}

    def extra_score(self, c):
        """
        Assign an extra score to c, depending on the rule
        """
        return 0.0

    def _compute_remaining_candidate_probability(self):
        """
        Compute the remaining items to be counted
        """
        remaining = copy.deepcopy(self._counting_dictionary(self._collector))
        candidates = {}
        for instructions in self._program.values():
            len_inst = self.candidate_count(instructions)
            if len_inst == 1:
                # Remove one of the available elements
                if not instructions[0].ignore:
                    for v in self._counting_field(instructions[0]):
                        remaining[v] -= 1
            else:
                # Count the candidates to obtain that element
                for c in instructions:
                    if not c.ignore:
                        for v in self._counting_field(c):
                            candidates[v] = candidates[v] + 1 if v in candidates else 1

        # Finally compute the probability of obtaining an element to each candidate
        for v in remaining:
            if v in remaining and v in candidates:
                self._scores[v] = remaining[v] / candidates[v]
            else:
                self._scores[v] = 0

    def recover(self, address):

        if len(self._scores) == 0:
            self._compute_remaining_candidate_probability()

        candidates, i, new_score = self._program[address], 0, []
        update = False
        for c in candidates:
            if not c.ignore:
                score = self.extra_score(c)
                fields = self._counting_field(c)
                len_fields = len(fields)
                for v in fields:
                    score += self._scores[v] / len_fields if v in self._scores else 0
                update |= self._update_candidate_score(c, score)
        return update

    def _counting_bin_size(self):
        """
        Size of the bin
        """
        pass

    def _counting_field(self, instruction):
        """
        Return the value of the field that is being counted
        """
        pass

    def _counting_dictionary(self, collector):
        """
        Return the dictionary containing the field being counted
        """
        pass

class ConditionalCount(CountingRule):
    """
    Class that enforces that the conditional count in the program abides to the metadata conditional count
    """
    def _counting_field(self, instruction):
        """
        Return the value of the field that is being counted
        """
        return [instruction.conditional_field]

    def _counting_dictionary(self, collector):
        """
        Return the dictionary containing the field being counted
        """
        return collector.condition_count

    @staticmethod
    def short_name():
        return "COND_COUNT"

class RegisterCount(CountingRule):
    """
    Class that enforces that the conditional count in the program abides to the metadata conditional count
    """
    def _counting_field(self, instruction):
        """
        Return the value of the field that is being counted
        """
        return instruction.registers_used()

    def _counting_dictionary(self, collector):
        """
        Return the dictionary containing the field being counted
        """
        return collector.storage_count

    def extra_score(self, c):
        if c.is_branch:
            return 0.000001
        else:
            return 0.0

    @staticmethod
    def short_name():
        return "REG_COUNT"

class InstructionCount(CountingRule):
    """
    Class that enforces that the instruction count in the program abides to the metadata conditional count
    """
    def _counting_field(self, instruction):
        """
        Return the value of the field that is being counted
        """
        return [instruction.opcode_field]

    def _counting_dictionary(self, collector):
        """
        Return the dictionary containing the field being counted
        """
        return collector.instruction_count

    @staticmethod
    def short_name():
        return "INST_COUNT"