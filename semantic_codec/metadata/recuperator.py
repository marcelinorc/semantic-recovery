from semantic_codec.metadata.collector import CorruptedProgramMetadataCollector
from semantic_codec.metadata.counting_rules import ConditionalCount, InstructionCount, RegisterCount
from semantic_codec.metadata.distance_rule import RegisterReadDistance
from semantic_codec.metadata.probabilistic_model import DefaultProbabilisticModel
from semantic_codec.metadata.rules import ControlFlowBehavior
from semantic_codec.probability.probabilities import indep_events_union, uniform
from semantic_codec.report.print_progress import TextProgressBar


class Recuperator(object):
    """
    Class in charge of recuperating the lost bits of information using the metadata sent
    """

    def __init__(self, collector, program, model=None):
        """
        Builds the recuperator
        :param collector: Metadata collector
        :param program: Dictionary where the key is the memory position of an instruction
                        and the value a list of possibles instructions.
        """
        self._collector = collector
        self._program = program

        # self._errors = 0
        # for pos, val in self._program.items():
        #    self._errors += len(val) - 1
        self.passes = 1
        self._model = DefaultProbabilisticModel() if model is None else model

    def _recover(self, progress_bar):
        for i in range(0, self.passes):
            rules = [ControlFlowBehavior(self._program),
                     ConditionalCount(self._program, collector=self._collector),
                     InstructionCount(self._program, collector=self._collector),
                     RegisterCount(self._program, collector=self._collector),
                     RegisterReadDistance(self._program, collector=self._collector)]

            for pos, instructions in self._program.items():
                if len(instructions) > 1:
                    for r in rules:
                        r.current_pass = i
                        r.recover(pos)
                # Find the mean value of scores:
                # k = len(instructions)
                if self.passes > 1 and len(instructions) > 1:
                    # k = 0
                    for inst in instructions:
                        for v in inst.scores_by_rule.values():
                            if v <= 0 and not inst.ignore:
                                inst.ignore = True

                progress_bar.suffix = 'Complete (Iteration: {})'.format(i)
                progress_bar.progress()

    def recover(self):
        """
        Start the recovery process
        """
        # scores_changed = True
        # while scores_changed:
        # scores_changed = False

        progress_bar = TextProgressBar(iteration=0, total=len(self._program.items()) * self.passes, prefix='Recovering:',
                                       decimals=0, bar_length=50, print_dist=4)
        self._recover(progress_bar)




def probabilistic_rules(scores_dict):

    pc = scores_dict['pc'] if 'pc' in scores_dict else 1
    pr = scores_dict['pr'] if 'pr' in scores_dict else 1
    prd = scores_dict['prd'] if 'prd' in scores_dict else 1
    po = scores_dict['po'] if 'po' in scores_dict else 1
    pfb = scores_dict['pfb'] if 'pfb' in scores_dict else 1
    pcb = scores_dict['pcb'] if 'pcb' in scores_dict else 1

    for k, p in scores_dict.items():
        if p > 1 or p < 0:
            raise RuntimeError('Invalid probability of rule {}: {} '.format(k, p))

    p = pc * pr * prd * po * (pfb + pcb - pfb * pcb)
    if p > 1 or p < 0:
        raise RuntimeError('Invalid probability: {} '.format(p))

    return p


class ProbabilisticRecuperator(Recuperator):
    def _pmf_register_distance(self, instruction):
        """
        Computes the probability that all the registers of a given instructions are read at this precise address
        :param instruction:
        :return:
        """
        add = instruction
        pass

    def _instruction_range_probs(self, addr, a, b, f):
        """
        Returs the list of approximate probability of instruction within a certain range of an instruction
        :param a: min distance (negative to say indicate a range of instructions before)
        :param b: max distance (negative to say indicate a range of instructions before)
        :return: a probability
        """
        ph = []

        r = -1 if b < a else 1
        for k in range(a, b, r):
            a = addr - 4 * k
            t, prb_union = 0, 0
            if a in self._program.keys():
                for ai in self._program[a]:
                    if not ai.ignore and ai.score() > 0 and f(ai):
                        t += 1
                        # Since only one inst can be selected, these are mutually exclusive events
                        prb_union += ai.score()
                if prb_union > 0:
                    ph.append(prb_union/t)
        return ph

    def _recover(self, progress_bar):
        # first, recopilate all the data we need once
        # This data consist in the amount of conditionals, operands and registers in the program

        cpmd = CorruptedProgramMetadataCollector()
        cpmd.collect(self._program)

        dist_min = self._collector.storage_min_dist
        dist_max = self._collector.storage_max_dist


        addresses = [ a for a in self._program.keys()]
        addresses.sort()

        for i in range(0, len(addresses)):
            addr = addresses[i]
            for inst in self._program[addr]:
                if inst.ignore:
                    continue

                inst.score_function = probabilistic_rules

                # Pc (Read the paper):
                c = inst.conditional_field
                o = inst.opcode_field
                r = inst.storages_used

                # See these probabilities expressed and explained in the paper
                try:
                    pc = self._collector.condition_count[c] / cpmd.address_with_cond[c]
                except KeyError:
                    pc = 0
                try:
                    po = self._collector.instruction_count[o] / cpmd.address_with_op[o]
                except KeyError:
                    po = 0
                try:
                    pr = self._collector.storage_count[c] / cpmd.address_with_reg[c]
                except KeyError:
                    pr = 0

                prd = 1

                # These probabilities take into consideration previous instructions,
                # therefore they cannot be applied to the first instruction
                if i > 0:
                    # Compute register distance
                    for r in inst.storages_read():
                        try:
                            a, b = dist_min[r], dist_max[r] + 1
                        except KeyError:
                            a, b = 0, 1

                        _pmf_reg_dist = uniform(a, b)
                        ph = self._instruction_range_probs(addr, b, a, lambda x: r in x.storages_written())

                        # Handle special registers such as SP, LP and PC
                        if r in [13, 15] and not ph:
                            # Do not take into consideration stack pointer read nor a program counter read
                            # PC not explicitly written and SP is very difficult to detect
                            continue
                        else:
                            prd *= indep_events_union([_pmf_reg_dist * p for p in ph]) if ph else 0

                    inst.scores_by_rule['prd'] = prd

                """
                    # Compute Flag/Branch rule
                    pfb = self._model.branch_after_cpsr  # This is a fixed probability
                    ph = self._instruction_range_probs(addr, 0, -1, lambda x: x.modifies_flags())
                    if ph:
                        pfb = indep_events_union([pfb * p for p in ph])
                        if not inst.is_branch:
                            pfb = 1 - pfb
                    else:
                        pfb = 1 - pfb if inst.is_branch else pfb


                    # Compute PCB
                    pcb = self._model.near_conditionals_are_equals  # This is a fixed probability
                    ph = self._instruction_range_probs(addr, 1, 2,
                                                       lambda x: x.conditional_field == inst.conditional_field)
                    if ph:
                        pcb = indep_events_union([pcb * p for p in ph])
                    else:
                        pcb = 1 - self._model.near_conditionals_are_equals

                    # Only instructions with previous instructions can have these
                    inst.scores_by_rule['pfb'] = pfb
                    inst.scores_by_rule['pcb'] = pcb
                """



                inst.scores_by_rule['pc'] = pc
                inst.scores_by_rule['pr'] = pr
                inst.scores_by_rule['po'] = po

            progress_bar.progress()
