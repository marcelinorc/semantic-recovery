
class DefaultProbabilisticModel(object):
    """
    Class containing the values assigned to the variables of the probabilities model
    """
    def __init__(self):

        self.low_probability = 0.001

        self.high_probability = 1 - self.low_probability

        # Observed probability of a push occurring if a pop is at the end and middle of the function
        self.push_given_pop_at_fn_end_equal_registers = 0.9999

        # Observed probability of a push occurring if a pop is at the end
        self.push_given_pop_at_fn_end = 0.7

        # Observed probability of a push occurring if a pop is at the middle of the function
        self.push_given_pop_at_fn_middle = 0.65

        # Observed probability of a push occurring if a pop is at the end and middle of the function
        self.push_given_pop_at_fn_end_and_middle = 0.89

        # Observed probability of a non-all to exists after a branch and all near conditional were equal
        self.branch_after_cpsr_and_near_cond_are_equals = 0.85

        # Observed probability of a non-all to exists after a branch and the previous conditional was equal
        self.branch_after_cpsr_and_prev_cond_are_equals = 0.65

        # Observed probability of a non-all to exists after a branch and the previous conditional was equal
        self.branch_after_cpsr_and_after_cond_are_equals = 0.76

        # Indicates the probability of a branching instruction happening after a flag register write
        self.branch_after_cpsr = 0.6

        # Indicates the probability that a instructions have the same conditional of its predecesor and sucesor
        self.both_conditionals_are_equals = 0.7

        # Indicates the probability that a instructions have the same conditional of its predecesor
        self.prev_conditionals_are_equals = 0.65

        # Indicates the chance of a jump being invalid if it lies inside the program
        self.just_any_jump_is_valid = self.low_probability

        # Indicates the chance of a jump branching to the same method
        self.branch_to_this_method = 0.67

        # Indicates the chance of a jump branching to the same method
        self.branch_to_other_method_start = 0.7