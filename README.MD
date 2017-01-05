# ARM Semantic Codec

Remotely reprogramming  network's devices to correct bugs in the firmware or to dynamically change their 
behavior, is an open research field in both IoT and WSN. One of the main challenges to achieve this goal
lies in sending a new software version to energy constrained devices for which reception of data is an 
energy-hungry operation. 
	
In this context, Forward Error Correction (FEC) is used to prevent energy consumption due to 
retransmission of lost packets in noisy environments. 
This paper introduces a FEC encoding tailored for ARM CPUs instructions. 
Our approach introduces **Recovery Semantics**, i.e. knowledge of ARM instructions structure and also 
insights on the program being sent to partially or even fully recover instructions inside a faulty 
packet.

### Dependencies: 
 - PyGraph: https://github.com/pmatiello/python-graph
 - DARM: https://github.com/jbremer/darm
 
 
 ### Notes on the use of functions:
 
 The use of functions to build the control flow graph and SSA form, instead of *builder* 
 classes makes sense because it improves testability as I can write tests
 to individual parts of the process,  without having to break encapsulation or
 having (in my opinion) "private method classes", that is, classes that only contain a public method that cannot be
 invoked unless certain prerequisites are meet and that are only going to be used in a certain context.