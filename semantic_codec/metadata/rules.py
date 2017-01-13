"""
File containing the classes representing rules
"""
import copy

from semantic_codec.architecture.arm_instruction import AOpType
from semantic_codec.metadata.collector import MetadataCollector


def from_instruction_list_to_dict(instructions):
    result = {}
    for inst in instructions:
        result[inst.position] = [inst]
    return result


class DefaultProbabilisticModel(object):
    """
    Class containing the values assigned to the probabilities model variables
    """

    def __init__(self):
        self.ALWAYS_AFTER_CPSR = 0.1
        self.NEAR_CONDITIONALS_ARE_EQUALS = 0.5


class Rule(object):
    def __init__(self, program, model=None):
        self._model = DefaultProbabilisticModel() if model is None else model
        self._program = program

    def recover(self, position):
        """
        Tries to recover an instruction in a given position of a program
        :param position: Position where the instruction is
        :param program: Program to recover
        :param model: Probabilistic model
        :return: The amount of instructions discarded
        """
        pass

    def _get_instruction_at(self, adrr, program):
        inst = None
        if adrr in adrr:
            inst = program[adrr]
        return inst

    def _update_scores(self, new_scores, instructions):
        """
        Determine if the scores assigned to the instructions by the rules have changed
        """
        i, k = 0, str(self.__class__)
        updated = False
        for inst in instructions:
            if k not in inst.scores_by_rule or new_scores[i] != inst.scores_by_rule[k]:
                inst.scores_by_rule[k] = new_scores[i]
                updated = True
            i += 1

        return updated


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
        return collector.register_count


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


class ConditionalFollowsCPSRModifier(Rule):
    """
    Class that enforces the rule that a conditional instruction must follow another capable of modifying the CPSR register
    """

    def recover(self, position):
        # Get previous instruction
        addr = position - 4
        prev_inst = self._program[addr] if addr in self._program else None
        # Get posterior instruction
        addr = position + 4
        post_inst = self._program[addr] if addr in self._program else None

        # Score assigned to each conditional field
        conditional_score = [0.0] * 16

        if prev_inst is not None and len(prev_inst) == 1:
            if prev_inst[0].modifies_flags():
                # Assign a BAD score to the conditional 'always' if we have
                # a previous instruction that modifies the flags
                conditional_score[AOpType.COND_ALWAYS] -= self._model.ALWAYS_AFTER_CPSR
            else:
                # Assign a good score to the conditional equal to the previous instruction
                conditional_score[prev_inst[0].conditional_field] += self._model.NEAR_CONDITIONALS_ARE_EQUALS
        if post_inst is not None and len(post_inst) == 1:
            # Assign a good score to the conditional equal to the posterior instruction
            conditional_score[post_inst[0].conditional_field] += self._model.NEAR_CONDITIONALS_ARE_EQUALS

        i, new_score = 0, []
        for c in self._program[position]:
            new_score.append(conditional_score[c.conditional_field])
        return self._update_scores(new_score, self._program[position])


class Recuperator(object):
    """
    Class in charge of recuperating the lost bits of information using the metadata sent
    """

    def __init__(self, collector, program):
        """
        Builds the recuperator
        :param collector: Metadata collector
        :param program: Dictionary where the key is the memory position of an instruction
                        and the value a list of possibles instructions.
        """
        self._collector = collector
        self._program = program

        self._rules = [ConditionalFollowsCPSRModifier()]
        # self._errors = 0
        # for pos, val in self._program.items():
        #    self._errors += len(val) - 1

    def recover(self):
        """
        Start the recovery process
        """
        scores_changed = True
        while scores_changed:
            scores_changed = False
            for pos, instructions in self._program.items():
                if len(instructions) > 1:
                    for r in self._rules:
                        scores_changed |= r.recover(pos, self._program)
