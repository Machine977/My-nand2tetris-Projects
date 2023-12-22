//init
@258
D=A
@SP
M=D

//init stack
@25
D=A
@256
M=D

@26
D=A
@257
M=D

//Equal command
@SP
AM=M-1 //Select top value, decrement stack
D=M //Store top value.
@SP
A=M-1 //Select bottom value.
D=M-D
@TRUE
D;JEQ //Jump to TRUE if bottom value - top value = 0.
//False
@SP
A=M-1
M=0
@END
0;JMP //Don't run TRUE, go straight to end since the answer is false.
(TRUE)
@SP
A=M-1
M=-1
(END)
