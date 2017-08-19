from semantic_codec.architecture.arm_constants import AReg
from semantic_codec.metadata.probabilistic_rules.counting_rules import ConditionalCount, InstructionCount, RegisterCount
from semantic_codec.metadata.probabilistic_rules.rules import ControlFlowBehavior

from semantic_codec.metadata.metadata_collector import CorruptedProgramMetadataCollector
from semantic_codec.metadata.probabilistic_model import DefaultProbabilisticModel
from semantic_codec.metadata.probabilistic_rules.distance_rule import RegisterReadDistance
from semantic_codec.report.print_progress import TextProgressBar


class Recuperator(object):
    """
    Class in charge of recuperating the lost bits of information using the metadata sent.

    DEPRECATED IN FAVOR OF ProbabilisticRecuperator
    """

    def __init__(self, collector, program, model=None, functions=None):
        """
        Builds the recuperator
        :param collector: Metadata collector
        :param program: Dictionary where the key is the memory position of an instruction
                        and the value a list of possibles instructions.
        """
        self._collector = collector
        self._program = program
        self._functions = functions if functions else {}

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


def probabilistic_rules(scores_dict, inst):
    # Conditional register score
    pc = scores_dict['pc'] if 'pc' in scores_dict else 1
    # Register score
    pr = scores_dict['pr'] if 'pr' in scores_dict else 1
    # Register distance score
    prd = scores_dict['prd'] if 'prd' in scores_dict else 1
    # Opcode score
    po = scores_dict['po'] if 'po' in scores_dict else 1
    # Proper control flow
    pcf = scores_dict['pcfg'] if 'pcfg' in scores_dict else 1
    # Push Pop score
    pupo = scores_dict['pupo'] if 'pupo' in scores_dict else 1
    # Branch distance score
    pbd = scores_dict['pbd'] if 'pbd' in scores_dict else 1
    # The basic score all instructions must abide to
    score = pc * po * pcf
    # In order to keep the competition fair, all instructions must have equal amount of optional scores
    if inst.is_branch:
        score *= pbd
    elif inst.is_push_pop:
        score *= pr * pupo
    else:
        score *= pr * prd
    if score > 1 or score < 0:
        raise RuntimeError('Invalid probability: {} '.format(score))
    return score


def probabilistic_rules_remove_step(scores_dict, inst):

    lo = 2
    for k, p in scores_dict.items():
        if p < lo:
            lo = p

    # Conditional register score
    pc = scores_dict['pc'] if 'pc' in scores_dict else 1
    # Register score
    pr = scores_dict['pr'] if 'pr' in scores_dict else 0
    # Register distance score
    prd = scores_dict['prd'] if 'prd' in scores_dict else 1
    # Opcode score
    po = scores_dict['po'] if 'po' in scores_dict else 1
    # Proper control flow
    pcf = scores_dict['pcfg'] if 'pcfg' in scores_dict else 1
    # Push Pop score
    pupo = scores_dict['pupo'] if 'pupo' in scores_dict else 1
    # Branch distance score
    pbd = scores_dict['pbd'] if 'pbd' in scores_dict else 1

    hi = max(pc, po, pr)
    # Register score again
    pr = scores_dict['pr'] if 'pr' in scores_dict else 0

    if hi == 1 and lo != 0:
        score = 1
    elif lo == 0 or inst.ignore:
        score = 0
    else:
        # The basic score all instructions must abide to
        score = pc * po * pcf
        # In order to keep the competition fair, all instructions must have equal amount of optional scores
        if inst.is_branch:
            score *= pbd
        elif inst.is_push_pop:
            score *= pr * pupo
        else:
            score *= pr * prd

    if score > 1 or score < 0:
        raise RuntimeError('Invalid probability: {} '.format(score))

    return score


class ProbabilisticRecuperator(Recuperator):
    def _pmf_register_distance(self, instruction):
        """
        Computes the probability that all the registers of a given instructions are read_instructions at this precise address
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

    def _compute_conditional(self, inst, cpmd):
        """
        Compute the probability that an instruction is awarded one conditional from the metadata
        """
        # Conditional field of the instruction
        c = inst.conditional_field
        # See these probabilities expressed and explained in the paper
        try:
            pc = self._collector.condition_count[c] / cpmd.address_with_cond[c]
        except KeyError:
            pc = 0
        inst.scores_by_rule['pc'] = pc

    def _compute_opcode(self, inst, cpmd):
        """
        Compute the probability that an instruction is awarded one opcode from the metadata
        """
        # Pc (Read the paper):
        o = inst.opcode_field
        # See these probabilities expressed and explained in the paper
        try:
            po = self._collector.instruction_count[o] / cpmd.address_with_op[o]
        except KeyError:
            po = 0
        inst.scores_by_rule['po'] = po

    def _compute_registers(self, inst, cpmd):
        """
        Compute the probability that this instruction is awarded all of its registers from the metadata
        """
        if inst.is_branch or inst.is_push_pop:
            return
        r = inst.storages_used()
        try:
            # Assuming independence is faster than the actual probabilities
            av = 1
            for rr in r:
                #av *= self._collector.storage_count[rr] / cpmd.address_with_reg[rr]
                av = min(av, self._collector.storage_count[rr] / cpmd.address_with_reg[rr])
            pr = av
        except KeyError:
            pr = 0
        inst.scores_by_rule['pr'] = pr

    def _prob_of_a(self, val, addr):
        c, t = 0, 0
        for i in self._program[addr]:
            if not i.ignore:
                t += 1
                # TODO: Include the register information
                if i.is_a(val):
                    c += 1
        return c / t if t > 0 else 0

    def _op_prob_and_check_equal_registers(self, opcode, addr, push_reg_readed):
        """
        This method computes the probability of a instruction with a given opcode of existing in an address.
        It also checks if it has the same registers than the ones given in push_reg_readed.
        Is ONLY meant for being called from _compute_push_pop
        """
        reg_equals_inst = False
        c, t = 0, 0
        for i in self._program[addr]:
            if not i.ignore:
                t += 1
                # Include the register information
                # i.e. we are looking for a pop with equal registers
                if i.is_a(opcode):
                    c += 1
                    if not reg_equals_inst:
                        a = True
                        pop_reg_read = i.registers_written()
                        for r in pop_reg_read:
                            if not (r in push_reg_readed or r is AReg.PC):
                                a = False
                                break
                        for r in push_reg_readed:
                            if not (r in pop_reg_read or r is AReg.LR or r is AReg.SP):
                                a = False
                                break
                        if a:
                            reg_equals_inst = True
        p1 = c / t
        return p1, reg_equals_inst

    def _compute_push_pop(self, inst, cpmd, addr, current_fn):
        """
        Push and pops have a peculiar behavior: Their are commonly found at the begining and at the end of a function
        to restore registers to their state before the calling of a method.

        This function computes a probabilistic value of this behavior actually occurring in the program being recovered.

        If the inst is a push, it searches for pops at the end of the function, or pops followed by branches somewhere
        in the middle.

        If the pops have equal register list, it rewards a high probability to the push instruction.

        A similar thing is done for pops
        """
        p1, p2, p3 = 0, 0, 0

        if inst.is_a('push'):
            # Is this is a push that lies in the start of the function?
            if addr in self._functions:
                push_reg_readed = inst.registers_read()

                last_addr = self._functions[addr][1]
                # If so, let's first try to find a pop at the end of the function
                #p1 = self._prob_of_a('pop', last_addr)

                p1, reg_equals = self._op_prob_and_check_equal_registers('pop', last_addr, push_reg_readed)

                # If a pop at the end was found, try to find another pop follow by a branch in previous inst
                cb1, cp1, tb1, tp1 = 0, 0, 0, 0
                cb2, tb2 = 0, 0
                p2 = 0
                for a in range(last_addr, addr, -4):
                    cb2 = cb1
                    tb2 = tb1
                    for i in self._program[a]:
                        if not i.ignore:
                            tb1 += 1
                            tp1 += 1
                            if i.is_branch:
                                cb1 += 1
                            if i.is_a('pop'):
                                cp1 += 1
                    if tb2 > 0 and tb1 > 0:
                        p2 = cp1 / tb1 * cb2 / tb2
                    if p2 > 0:
                        break
            else:
                reg_equals = False
        elif inst.is_a('pop'):
            reg_written = inst.registers_written()
            p1, reg_equals = self._op_prob_and_check_equal_registers('push', current_fn, reg_written)
        else:
            return None

        p3 = 1 / len(self._program[addr])
        if reg_equals:
            p3 = self._model.push_given_pop_at_fn_end_equal_registers
        if p1 > 0:
            p1 = self._model.push_given_pop_at_fn_end
        if p2 > 0:
            p2 = self._model.push_given_pop_at_fn_middle

        inst.scores_by_rule['popu'] = max(p1, p2, p3)

    def _compute_proper_cfg(self, inst, cpmd, addr):
        """
        Computes the probability of this instruction of being placed in a proper place in the control flow.
        This means that (i) its surrounded by equal conditionals OR that it (ii) branch after a flag modify
        """

        ###################################################
        # THE INSTRUCTION IS PLACED NEAR SAME CONDITIONAL
        ###################################################

        # Compute the probability of the previous instruction having equal conditinoal
        a = addr - 4
        prev_inst = self._program[a] if a in self._program else None
        # Get posterior instruction
        a = addr + 4
        post_inst = self._program[a] if a in self._program else None

        # The previous instruction has an score computed. We use that
        prev = 0
        # Previous instructions with the same conditional
        same_cond = 0
        # Instructions modifiying the flag register
        flag_mod = 0
        # Instructions both having the same conditional and modifying the registers
        union_count = 0
        # Posterior instructions with the same conditional
        after_same_cond = 0



        ln_prev = 0
        ln_post = 0

        if prev_inst:
            for i in prev_inst:
                if not i.ignore:
                    ln_prev += 1
                    a = i.conditional_field == inst.conditional_field
                    b = AReg.CPSR in i.registers_written()
                    if a:
                        same_cond += 1
                    if b:
                        flag_mod += 1
                    # COMPUTE THE UNION OF BOTH EVENTS
                    if a and b:
                       union_count += 1

        # Compute the probability of the following instruction having equal conditinal
        after = 0
        if post_inst:
            after_same_cond = 0
            for i in post_inst:
                if not i.ignore:
                    ln_post += 1
                    if i.conditional_field == inst.conditional_field:
                        after_same_cond += 1

        all_conditional = 14
        p1, p2, p3 = 0, 0, 0
        result = 0
        if inst.conditional_field != all_conditional:
            if same_cond > 0 and flag_mod > 0:
                if after_same_cond > 0:
                    p1 = (same_cond + flag_mod - union_count) * after_same_cond / (ln_prev * ln_post)
                    p1 *= self._model.branch_after_cpsr_and_near_cond_are_equals

                p2 = (same_cond + flag_mod - union_count) / ln_prev
                p2 *= self._model.branch_after_cpsr_and_prev_cond_are_equals

                result = max(p1, p2)

            elif same_cond > 0:
                if after_same_cond > 0:
                    p1 = same_cond * after_same_cond / (ln_prev * ln_post)
                    p1 *= self._model.both_conditionals_are_equals

                p2 = same_cond / len(prev_inst)
                p2 *= self._model.prev_conditionals_are_equals
                result = max(p1, p2)

            elif flag_mod > 0:
                if after_same_cond > 0:
                    p1 = flag_mod * after_same_cond / (ln_prev * ln_post)
                    p1 *= self._model.branch_after_cpsr_and_after_cond_are_equals

                p2 = flag_mod / ln_prev
                p2 *= self._model.branch_after_cpsr
                result = max(p1, p2)
        else:
            if flag_mod > 0:
                p3 = flag_mod / ln_prev
                p3 *= 1 - self._model.branch_after_cpsr
                result = p3
            elif same_cond > 0:
                if after_same_cond > 0:
                    p1 = same_cond * after_same_cond / (ln_prev * ln_post)
                    p1 *= self._model.both_conditionals_are_equals
                p2 = same_cond / len(prev_inst)
                p2 *= self._model.prev_conditionals_are_equals
                result = max(p1, p2)
            elif after_same_cond > 0:
                p1 = after_same_cond / ln_post
                p1 *= self._model.prev_conditionals_are_equals
                result = p1

        if result == 0:
            result = self._model.low_probability
        elif result > 1:
            raise RuntimeError('Invalid probability')

        inst.scores_by_rule['pcfg'] = result

    def _compute_register_distance(self, inst, cpmd, addr):
        # These probabilities take into consideration previous instructions,
        # therefore they cannot be applied to the first instruction
        # Dictionary with the minimum register distance

        if inst.is_branch or inst.is_push_pop:
            return

        dist_min = self._collector.storage_min_dist
        dist_max = self._collector.storage_max_dist

        prd = 1
        # Compute register distance
        for r in inst.storages_read():
            try:
                a, b = dist_min[r], dist_max[r] + 1
            except KeyError:
                a, b = 0, 1

            max_dist = addr - 4 * b
            min_dist = addr - 4 * a

            p = 1
            for a in range(max_dist, min_dist):
                count = 0
                t = 0
                if not a in self._program:
                    continue

                for x in self._program[a]:
                    if not x.ignore:
                        t += 1
                        if r in x.storages_written():
                            count += 1
                if t > 0:
                    p *= 1 - count / t
                    if p == 1:
                        break

            prd = min(p, prd)
            if prd >= 1:
                prd = self._model.high_probability
                break
        prd = 1 - prd
        if prd <= 0:
            prd = self._model.low_probability
        inst.scores_by_rule['prd'] = prd
#                _pmf_reg_dist = uniform(a, b)
#                ph = self._instruction_range_probs(addr, b, a, lambda x: )
                # Handle special registers such as SP, LP and PC
#                if r in [13, 15] and not ph:
                    # Do not take into consideration stack pointer read_instructions nor a program counter read_instructions
                    # PC not explicitly written and SP is very difficult to detect
#                    continue
#                else:
#                    prd *= indep_events_union([_pmf_reg_dist * p for p in ph]) if ph else 0


    def _compute_branch_address(self, inst, current_fn, lowest_addr, highest_addr):
        """
        Branching is not random. A branch should occur inside the method or to the beginning of another method.

        This method analyzes the branching address of a branch instruction and then provides a probability of
        the address being correct
        """
        if inst.ignore or not inst.is_branch:
            return
        jmp_addr = inst.jumping_address

        if jmp_addr is None:
            # It might be possible that the address is computed dynamically,
            # therefore the jmp_address will be unknown
            inst.scores_by_rule['pbd'] = self._model.just_any_jump_is_valid * 2
        # Award high prob to addresses inside this method or to the begin of other methods
        elif jmp_addr >= current_fn and jmp_addr <= self._functions[current_fn][1]:
            inst.scores_by_rule['pbd'] = self._model.branch_to_this_method
        # Award medium-high prob to a branch to the start of other method
        elif jmp_addr in self._functions:
            inst.scores_by_rule['pbd'] = self._model.branch_to_other_method_start
        # Award low prob to addresses outside the program
        elif jmp_addr > highest_addr or jmp_addr < lowest_addr:
            inst.scores_by_rule['pbd'] = self._model.just_any_jump_is_valid
        # Award low to med prob to anithing else
        else:
            inst.scores_by_rule['pbd'] = self._model.just_any_jump_is_valid * 2

    def _recover(self, progress_bar):
        # first, recopilate all the data we need once
        # This data consist in the amount of conditionals, operands and registers in the program

        cpmd = CorruptedProgramMetadataCollector()
        cpmd.collect(self._program)

        # Order addresses so we are sure we go from lower addresses to higher addresses
        addresses = [a for a in self._program.keys()]
        addresses.sort()

        lowest_addr = addresses[0]
        highest_addr = addresses[len(addresses) - 1]
        current_fn = addresses[0]

        for i in range(0, len(addresses)):
            addr = addresses[i]
            if addr in self._functions:
                current_fn = addr
            for inst in self._program[addr]:
                if inst.ignore:
                    continue

                # Sets the probabilistic rures function as the score calculation of the intruction
                inst.score_function = probabilistic_rules_remove_step

                self._compute_conditional(inst, cpmd)
                self._compute_opcode(inst, cpmd)
                self._compute_registers(inst, cpmd)
                self._compute_push_pop(inst, cpmd, addr, current_fn)
                self._compute_branch_address(inst, current_fn, lowest_addr, highest_addr)
                if i > 0:
                    self._compute_register_distance(inst, cpmd, addr)
                    self._compute_proper_cfg(inst, cpmd, addr)
            progress_bar.progress()

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

