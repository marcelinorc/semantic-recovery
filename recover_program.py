import os
from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.corruption.corruptor import corrupt_program
from semantic_codec.metadata.collector import MetadataCollector
from semantic_codec.metadata.recuperator import Recuperator
from semantic_codec.metadata.rules import from_instruction_list_to_dict


def run_recovery(path):
    # Read the program from file
    program = TextDisassembleReader(path).read()
    # Collect the metrics on it
    collector = MetadataCollector()
    collector.collect(program)
    program = from_instruction_list_to_dict(program)
    # Corrupt it:
    corrupt_program(program, 10.0, 3)

    # Recover it:
    r = Recuperator(collector, program)
    r.recover()

    for v in program.values():
        v.sort(key=lambda x: x.score(), reverse=True)
        s = " -- "
        for i in v:
            s += str(i) + " -- "
        print(s)

if __name__ == "__main__":
    ARM_SIMPLE = os.path.join(os.path.dirname(__file__), 'tests/data/dissasembly.armasm')
    run_recovery(ARM_SIMPLE)