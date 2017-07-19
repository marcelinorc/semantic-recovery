import os
from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.corruption.corruption import corrupt_program, save_corrupted_program_to_json, \
    load_corrupted_program_from_json
from semantic_codec.corruption.corruptors import JSONCorruptor, RandomCorruptor, PacketCorruptor, DARMInstruction, sys
from semantic_codec.metadata.collector import MetadataCollector
from semantic_codec.metadata.recuperator import Recuperator, ProbabilisticRecuperator
from semantic_codec.metadata.rules import from_instruction_list_to_dict, from_instruction_dict_to_list

def print_report(instructions_output_file, recovered_program):
    errors, recovered, fail_looses, fail_tide = 0, 0, 0, 0
    orig_stdout = sys.stdout
    f = open(instructions_output_file, 'w')
    sys.stdout = f

    bad_rules = {}
    aver_instr_tie_sum = 0
    aver_instr_tie_count = 0

    for i in range(0, len(original_program)):
        s = ""
        print('Original Instruction: {}'.format(original_program[i]))
        instructions = recovered_program[i]

        addr = original_program[i].position

        ori_inst = None
        for inst in instructions:
            if inst.encoding == original_program[i].encoding:
                ori_inst = inst
                break

        if len(instructions) > 1:
            instructions.sort(key=lambda x: x.score(), reverse=True)
            errors += 1
            ori_str = str(original_program[i])
            c1_str = str(instructions[0])
            c2_str = str(instructions[1])
            if c1_str != ori_str:
                print(" * FAIL : 1st Instruction is not original. ")
                print(" * WRONG SCORES [Recovered vs Original]:")
                # Print the comparison with the original rule
                for k, v in instructions[0].scores_by_rule.items():
                    try:
                        ov = ori_inst.scores_by_rule[k]
                        if v > ov:
                            print(" -> {0!s}: {1:.6f} vs. {2:.6f} ".format(k, v, ov))
                            bad_rules[k] = bad_rules[k] + 1 if k in bad_rules else 1

                    except KeyError:
                        print(" KE: {} -- ".format(k), end="")
                print()

                fail_looses += 1
            elif instructions[0].score() == instructions[1].score() and c1_str != c2_str:
                inst_count = 0
                while inst_count < len(instructions) and \
                                instructions[0].score() == instructions[inst_count].score():
                    inst_count += 1
                print(' * TIE : {} instructions with good score'.format(inst_count))
                aver_instr_tie_sum += inst_count
                aver_instr_tie_count += 1
                fail_tide += 1
            else:
                recovered += 1
                print(" * OK!")

            for inst in instructions:
                if inst.ignore:
                    print("X", end="")
                if inst.encoding == original_program[i].encoding:
                    print("{3} ++ [{2}] {0!s} : {1:.6f}: --> ".format(inst, inst.score(), inst.encoding, addr), end="")
                else:
                    print("{3} -- [{2}] {0!s} : {1:.6f}: --> ".format(inst, inst.score(), inst.encoding, addr), end="")
                for k, v in inst.scores_by_rule.items():
                    print(" {0!s}: {1:.6f} -- ".format(k, v), end="")
                print("")
        print("------------")

    print("------------")

    print('BAD RULES:')
    if len(bad_rules) == 0:
        print('No rule assigned a higher score to a false winner')
    for k, v in bad_rules.items():
        print('{} : {}'.format(k, v))

    if aver_instr_tie_count > 1:
        print("------------")
        print('AVERAGE TIE COUNT: {}'.format(aver_instr_tie_sum/aver_instr_tie_count))

    print("------------")

    print("ERRORS: {} -- LOSING: {} -- TIDE: {} --RECOVERED: {} -- RATIO: {} ".format(
        errors, fail_looses, fail_tide, recovered, recovered / errors))

    sys.stdout = orig_stdout


def run_recovery(original_program, corruptor, recuperator, passes=1):
    # Clone the original program
    program = [DARMInstruction(v.encoding, position=v.position) for v in original_program]

    # Collect the metrics on it
    collector = MetadataCollector()
    collector.collect(program)

    print("[INFO]: Metrics collected")

    # Corrupt it:
    program = corruptor.corrupt(from_instruction_list_to_dict(program))
    print("[INFO]: Program corrupted")

    # Recover it:
    r = recuperator(collector, program)
    r.passes = passes
    r.recover()
    print("[INFO]: Program recovered")

    return from_instruction_dict_to_list(program)


# max_error_per_instruction, corrupted_program=None, generate_new=False, )
if __name__ == "__main__":
    use_packets = True
    use_file = True
    recovered_program = None
    corruptor = None

    # ARM_SIMPLE = os.path.join(os.path.dirname(__file__), 'tests/data/dissasembly.armasm')
    ARM_SIMPLE = os.path.join(os.path.dirname(__file__), 'tests/data/helloworld.armasm')
    original_program = TextDisassembleReader(ARM_SIMPLE).read()

    if not use_file:
        if use_packets:
            ll = len(original_program)
            packet_count = ll / 32
            corruptor = PacketCorruptor(packet_count, ll, packets_lost=[3])
        else:
            corruptor = RandomCorruptor(30.0, 3, True)
    else:
        corruptor = JSONCorruptor()

    corruptor.corrupted_program_path = os.path.join(os.path.dirname(__file__), 'corrupted.json')
    #recovered_program = run_recovery(original_program, corruptor, Recuperator, 2)
    recovered_program = run_recovery(original_program, corruptor, ProbabilisticRecuperator)
    print_report('instructions.txt', recovered_program)