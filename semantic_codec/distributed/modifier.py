"""
Script that takes a program and starts modifying instructions so the efficacy of traditional compressors is improved.

The script modifies the ARM program and then sends a message to a server running in ARM to test if the program
produces a correct output
"""

#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#
import struct

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
for request in range(10):
    print("Sending request %s ..." % request)
    socket.send(b"Hello")
    #socket.send(struct.pack('<LL', 10, 10))

    #  Get the reply.
    message = socket.recv()
    print("Received reply %s [ %s ]" % (request, message))
