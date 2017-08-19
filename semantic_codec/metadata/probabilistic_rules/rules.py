"""
File containing the classes representing rules
"""
from semantic_codec.architecture.arm_instruction import AOpType
from semantic_codec.metadata.probabilistic_model import DefaultProbabilisticModel


def from_instruction_dict_to_list(program):
    keys = []
    keys.extend(program.keys())
    keys.sort()
    result = []
    result.extend([program[k] for k in keys])
    return result


def from_instruction_list_to_dict(instructions):
    """
    Turn the list of instructions into a dictionary indexed by position
    """
    result = {}
    for inst in instructions:
        result[inst.position] = [inst]
    return result


def from_functions_to_list_and_addr(functions):
    result = []
    fns = {}

    for f in functions:
        fns[f.start_addr()] = (f.start_addr(), f.final_addr())
        for inst in f.instructions:
            result.append(inst)

    result.sort(key=lambda x: x.position)

    return result, fns


class Rule(object):

    def __init__(self, program, model=None, collector=None):
        self._model = DefaultProbabilisticModel() if model is None else model
        self._program = program
        self._collector = collector
        self.current_pass = 1

    @staticmethod
    def short_name():
        return "Rule"

    def candidate_count(self, instructions):
        """
        Count the amount of valid candidates
        :param instructions:
        :return:
        """
        result = 0
        for inst in instructions:
            if not inst.ignore:
                result += 1
        return result

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

    def _update_candidate_score(self, candidate, new_score):
        k = self.short_name() + str(self.current_pass)
        if k not in candidate.scores_by_rule or new_score != candidate.scores_by_rule[k]:
            candidate.scores_by_rule[k] = new_score
            return True
        return False

    def _update_scores(self, new_scores, instructions):
        """
        Determine if the scores assigned to the instructions by the rules have changed
        """
        i, k = 0, self.short_name() + str(self.current_pass)
        updated = False
        for inst in instructions:
            if k not in inst.scores_by_rule or new_scores[i] != inst.scores_by_rule[k]:
                inst.scores_by_rule[k] = new_scores[i]
                updated = True
            i += 1

        return updated


# ------------------------------------------------------

class ControlFlowBehavior(Rule):
    """
    Class that enforces rewards instructions following a good control flow behavior:
    1 - Conditionals follow a flag register modifier instruction
    2 - Conditionals are usually group together
    TODO: 3 - Jump conditions are likelly to be found after comparison
    """

    @staticmethod
    def short_name():
        return "CFG"

    def recover(self, position):
        EPSILON = 0.00000000000001
        COND_TYPES = 16

        # TODO: Give some probability to instructions when they are candidates

        # Get previous instruction
        addr = position - 4
        prev_inst = self._program[addr] if addr in self._program else None
        # Get posterior instruction
        addr = position + 4
        post_inst = self._program[addr] if addr in self._program else None

        # Score assigned to each conditional field
        conditional_score = [EPSILON] * COND_TYPES
        pre_cond_count = [EPSILON] * COND_TYPES
        post_cond_count = [EPSILON] * COND_TYPES
        flag_mod, t_prev, t_post = 0, 0, 0
        if prev_inst is not None:
            for c in prev_inst:
                if not c.ignore:
                    pre_cond_count[c.conditional_field] += 1
                    if c.modifies_flags():
                        flag_mod += 1
                    t_prev += 1
        if post_inst is not None:
            for c in post_inst:
                if not c.ignore:
                    post_cond_count[c.conditional_field] += 1
                    t_post += 1

        if t_prev > 0:
            conditional_score[AOpType.COND_ALWAYS] -= self._model.branch_after_cpsr * flag_mod / t_prev
            # Assign a good score to the conditional equal to the previous instruction
            for i in range(0, COND_TYPES):
                conditional_score[i] += self._model.both_conditionals_are_equals * pre_cond_count[i] / t_prev
        if t_post > 0:
            # Assign a good score to the conditional equal to the posterior instruction
            for i in range(0, COND_TYPES):
                conditional_score[i] += self._model.both_conditionals_are_equals * post_cond_count[i] / t_post



        i, new_score = 0, []
        for c in self._program[position]:
            if not c.ignore:
                if c.is_branch:
                    # TODO: Improve the resolution of the jumping address
                    if c.jumping_address in self._program:
                        new_score.append(conditional_score[c.conditional_field] + self._model.just_any_jump_is_valid)
                    else:
                        new_score.append(conditional_score[c.conditional_field])
                else:
                    new_score.append(conditional_score[c.conditional_field])
            else:
                new_score.append(0.0)
        return self._update_scores(new_score, self._program[position])
