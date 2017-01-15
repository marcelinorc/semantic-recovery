import copy

from semantic_codec.metadata.rules import Rule


class CountingRule(Rule):

    def __init__(self, program, model=None, collector=None):
        super().__init__(program, model)
        if collector is None:
            raise RuntimeError("Needs a metadata collector")
        self._collector = collector
        self._remaining = copy.deepcopy(self._counting_dictionary(self._collector))

    def total_remaining(self):
        result = 0
        for v in self._remaining.values():
            result += v
        return result

    def _compute_remaining(self):
        """
        Compute the remaining items to be counted
        """
        for inst in self._program.values():
            if len(inst) == 1 and not inst[0].is_undefined:
                # Reduce the remaining amount of items in the field being counted
                for v in self._counting_field(inst[0]):
                    self._remaining[v] -= 1

    def recover(self, address):

        if self.total_remaining() == 0:
            return False
        self._compute_remaining()
        t = self.total_remaining()

        # Score assigned to each conditional field
        scores = {}
        for k in self._remaining:
            scores[k] = self._remaining[k] / t

        candidates, i, new_score = self._program[address], 0, []
        for c in candidates:
            inst_score, vals = 0, self._counting_field(c)
            for v in vals:
                inst_score += scores[v] if v in scores else 0
            new_score.append(inst_score)
        return self._update_scores(new_score, candidates)

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