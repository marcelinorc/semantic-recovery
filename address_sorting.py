import numpy as np
import matplotlib.pyplot as plt

def hi_in_hi(x, y, z):
    return x * 32 * 4 + y * 4 + z


def low_in_hi(x, y, z):
    return x * 32 * 64 + y * 64 + z


def print_lo_first_loose_high_bit():
    # Hi first and we start loosing in the high bit
    for z in range(0, 4):
        for y in range(0, 32):
            for x in range(0, 64):
                print(low_in_hi(x, y, z))

def print_hi_first_start_loosing_low_bit():
    # Hi first and we start loosing in the high bit
    for x in range(0, 64):
        for y in range(0, 32):
            for z in range(0, 4):
                print(hi_in_hi(x, y, z))

def print_hi_first_start_loosing_hi_bit():
    # Hi first and we start loosing in the high bit
    for z in range(0, 4):
        for y in range(0, 32):
            for x in range(0, 64):
                print(hi_in_hi(x, y, z))

print_hi_first_start_loosing_hi_bit()