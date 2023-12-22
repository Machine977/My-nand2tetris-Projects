//init
@258
D=A
@SP
M=D

//init stack
@10
D=A
@256
M=D

@5
D=A
@257
M=D

//And command
@SP
AM=M-1 //Select top value, decrement stack
D=M //Store top value.
@SP
A=M-1 //Select bottom value.
M=M&D