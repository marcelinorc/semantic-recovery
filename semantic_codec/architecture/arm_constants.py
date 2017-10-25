from semantic_codec.architecture.bits import Bits


class AReg:
    """
    ARM registers names. The cryptic AOp name is to have short code
    """
    R0 = 0
    R1 = A1 = 1
    R2 = A2 = 2
    R3 = A3 = 3
    R4 = V1 = 4
    R5 = V2 = 5
    R6 = V3 = 6
    R7 = WR = V4 = 7
    R8 = V5 = 8
    R9 = SB = V6 = 9
    R10 = SL = V7 = 10
    R11 = FP = V8 = 11
    R12 = IP = 12
    R13 = SP = 13
    R14 = LR = 14
    R15 = PC = 15
    # The store is modeled as a register
    STORE = 16
    # The flag register
    CPSR = 17
    # A fictitious register that is used to even the maths. The NOREG is the
    # register used by the instructions that use NO REGisters at all
    NOREG = 18

    STORAGE_NAMES = ["R{}".format(x) for x in range(0, NOREG)]
    STORAGE_NAMES.extend(['STORE', 'CPSR'])
    STORAGE_COUNT = len(STORAGE_NAMES)

    CAPSTONE_REGS = {
        0: 0, # No register
        66: R0,  # ARM_REG_R0 =
        67: R1,  # ARM_REG_R1 =
        68: R2,  # ARM_REG_R2 =
        69: R3,  # ARM_REG_R3 =
        70: R4,  # ARM_REG_R4 =
        71: R5,  # ARM_REG_R5 =
        72: R6,  # ARM_REG_R6 =
        73: R7,  # ARM_REG_R7 =
        74: R8,  # ARM_REG_R8 =
        75: R9,  # ARM_REG_R9 =
        76: R10, #ARM_REG_R10 =
        77: R11, #ARM_REG_R11 =
        78: R12,  #ARM_REG_R12 =
        10: LR,  #ARM_REG_LR =
        11: PC,  #ARM_REG_PC =
        12: SP,  # ARM_REG_SP =
    }

class AOp(object):
    """
    ARM Opcodes and opcode types. The cryptic AOp name is to have short code
    """
    AND = 0b0000 << 21
    EOR = 0b0001 << 21
    SUB = 0b0010 << 21
    RSB = 0b0011 << 21
    ADD = 0b0100 << 21
    ADC = 0b0101 << 21
    SBC = 0b0110 << 21
    RSC = 0b0111 << 21
    TST = 0b1000 << 21
    TEQ = 0b1001 << 21
    CMP = 0b1010 << 21
    CMN = 0b1011 << 21
    ORR = 0b1100 << 21
    BIC = 0b1110 << 21
    MOV = 0b1101 << 21
    MVN = 0b1111 << 21


class AOpType(object):
    """
    ARM Opcodes types. The cryptic AOpType name is to have short code
    """
    ALWAYS = Bits.set(31, 29)
    COND_ALWAYS = 0b1110

    LOAD_STORE_MULTIPLE = Bits.on(27)
    LOAD_STORE = Bits.on(26)
    LOAD_STORE_OFFSET = Bits.set(26, 25)
    SOFT_INTERRUPT = 0xF000000
    BRANCH = 0xA000000
    DATA_PROCESSING = 0x0
    DATA_PROCESSING_IMMEDIATE = 0x2000000