import os
from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.corruption.corruption import corrupt_program, save_corrupted_program_to_json, \
    load_corrupted_program_from_json
from semantic_codec.corruption.corruptors import JSONCorruptor, RandomCorruptor, PacketCorruptor, DARMInstruction
from semantic_codec.metadata.collector import MetadataCollector
from semantic_codec.metadata.recuperator import Recuperator
from semantic_codec.metadata.rules import from_instruction_list_to_dict, from_instruction_dict_to_list


def run_recovery(original_program, corruptor):
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
    r = Recuperator(collector, program)
    r.passes = 2
    r.recover()
    print("[INFO]: Program recovered")

    recovered_program = from_instruction_dict_to_list(program)

    errors, recovered, fail_looses, fail_tide = 0, 0, 0, 0

    for i in range(0, len(original_program)):
        s = ""
        print(original_program[i])
        instructions = recovered_program[i]
        if len(instructions) > 1:
            instructions.sort(key=lambda x: x.score(), reverse=True)
            errors += 1
            ori_str = str(original_program[i])
            c1_str = str(instructions[0])
            c2_str = str(instructions[1])
            if c1_str != ori_str:
                print(" - FAIL : 1st Instruction is not original")
                fail_looses += 1
            elif instructions[0].score() == instructions[1].score() and c1_str != c2_str:
                print(" - FAIL : Multiple instructions with good score")
                fail_tide += 1
            else:
                recovered += 1
                print(" - OK!")

            for inst in instructions:
                if inst.ignore:
                    print("X", end="")
                if inst.encoding == original_program[i].encoding:
                    print(" ++ [{2}] {0!s} : {1:.6f}: --> ".format(inst, inst.score(), inst.encoding), end="")
                else:
                    print(" -- [{2}] {0!s} : {1:.6f}: --> ".format(inst, inst.score(), inst.encoding), end="")
                for k, v in inst.scores_by_rule.items():
                    print(" {0!s}: {1:.6f} -- ".format(k, v), end="")
                print("")

    print("------------")
    print("ERRORS: {} -- LOSING: {} -- TIDE: {} --RECOVERED: {} -- RATIO: {} ".format(
        errors, fail_looses, fail_tide, recovered, recovered / errors))


# max_error_per_instruction, corrupted_program=None, generate_new=False, )
if __name__ == "__main__":
    use_packets = True
    # ARM_SIMPLE = os.path.join(os.path.dirname(__file__), 'tests/data/dissasembly.armasm')
    ARM_SIMPLE = os.path.join(os.path.dirname(__file__), 'tests/data/helloworld.armasm')
    original_program = TextDisassembleReader(ARM_SIMPLE).read()
    try:
        if use_packets:
            ll = len(original_program)
            packet_count = ll / 32
            run_recovery(original_program, PacketCorruptor(packet_count, ll, packets_lost=[1, 2, 3]))
        else:
            CORRUPTED = os.path.join(os.path.dirname(__file__), 'corrupted.json')
            run_recovery(original_program, JSONCorruptor(CORRUPTED))
    except FileNotFoundError:
        CORRUPTED = None
        run_recovery(original_program, RandomCorruptor(30.0, 3, True))
