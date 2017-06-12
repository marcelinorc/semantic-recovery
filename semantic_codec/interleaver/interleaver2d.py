from math import sqrt, fmod, floor, log
import numpy


def sp(m):
    """
    Performs the sucesive packing algorithm in a matrix. Which creates a 4^m X 4 ^m matrix of interleaved numbers
    :param m: Exponent to create the matrix.
    :return:
    """
    matrix = numpy.zeros(m, m)

    ul, ur, ll, lr = (0, 0), (1, 0), (0, 1), (1, 1)
    for n in range(1, m + 1):
        # Indexes
        w = 4 ** n

        # 4x + 2 quadrant (upper right)
        for i in range(w, w + w):
            for j in range(0, n):
                matrix[i, j] = matrix[i - w, j] * 4 + 2

        # 4x + 3 (lower left)
        for i in range(0, w):
            for j in range(w, w + w):
                matrix[i, j] = matrix[i, j - w] * 4 + 2

        # 4x + 1 (lower right)
        for i in range(w, w + w):
            for j in range(w, w + w):
                matrix[i, j] = matrix[i, j - w] * 4 + 2

        # 4x quadrant (upper left)
        for i in range(0, w):
            for j in range(0, n):
                matrix[i, j] *= 4


def build_2D_interlave_SP(packets):
    """
    Builds a 4^nx4^n matrix
    :param packets:
    :return:
    """
    # Find a 4^m X 4^m such as 4^m is the closest power of 4 smaller than the packet size
    while packets <= 0:
        matrix_size = 4 ** floor(log(packets, 4))

        # Build several matrix of this size
        matrix_count = floor(packets / matrix_size)

        # Compute remaining packets
        packets = fmod(packets, matrix_size)

        # Interleave matrixs columns to increase interleave


def build_2D_interleave_matrix_blaum(message_size, packet_size, data_width=-1, data_height=-1):
    """
    Produces a 2D interleaved matrix based in the results described in
    'Interleaving Schemes for Multidimensional Cluster Errors' by Blaum, Bruck and Vardy
    as well in the results provided in https://oeis.org/A047838,
    which are further explained in https://oeis.org/A047838/a047838.txt.

    Example for t == 3.

    1. Create two matrices
     A          B
    1 2 3 |  9  10 11
    4 5 6 |  12 13 14
    7 8 9 |  15 16 17

    2. Create a checkboard with these matrices:
     A B
     B A

    3. Interleave columns and rows aiming at making the sum of the differences maximal

    :param packet_size: Size of the packet (the unit does not matter as long as is the same as the message_size)
    :param message_size: Size of the message (the unit does not matter as long as is the same as the packet_size)
    :param data_width: Width of the data measured in the amount of packets per row. (It is  2D data, so it has width)
    :param data_height: Height of the data measured in the amount of packets per column.
     """

    if data_width != -1 and data_height == -1:
        data_height = round(message_size / data_width)
    elif data_height != -1 and data_width == -1:
        data_width = round(message_size / data_height)
    elif data_height == -1 and data_width == -1:
        raise RuntimeError('Cannot infer both data with and height')

    m = round(message_size / packet_size)
    b = round(sqrt(2 * m - 1))

    return [[int(abs(fmod(x - y * b, m))) for x in range(data_width)] for y in range(data_height)]


def interleave(data, matrix):
    """
    Interleaves data given an interleave matrix
    :param data:
    :param matrix:
    :return:
    """

# for k in range(0, 3):
#    for i in range(0, n):
#        print("{} {} {} {} {} {}".format(matrix1[i], matrix2[i], matrix1[i], matrix2[i], matrix1[i], matrix2[i]))
#
# print("------")
#
# for i in range(0, n, 2):
#    for j in range(0, n, 2):
#        m = matrix1[i][j]
#        matrix1[i][j] = matrix2[i][j]
#        matrix2[i][j] = m
#
# for k in range(0, 3):
#    for i in range(0, n):
#        print("{} {} {} {} {} {}".format(matrix1[i], matrix2[i], matrix1[i], matrix2[i], matrix1[i], matrix2[i]))
#
# print("------")
#
# for i in range(0, n - 1, 2):
#    for j in range(0, n - 2):
#        m = matrix1[j][i]
#        matrix1[j][i] = matrix1[n - j - 1][i]
#        matrix1[n - j - 1][i] = m
#
#        m = matrix2[j][i]
#        matrix2[j][i] = matrix2[n - j - 1][i]
#        matrix2[n - j - 1][i] = m
#
# for k in range(0, 3):
#    for i in range(0, n):
#        print("{} {} {} {} {} {}".format(matrix1[i], matrix2[i], matrix1[i], matrix2[i], matrix1[i], matrix2[i]))
