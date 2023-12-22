//This is for the "hard" solution, see the onenote.
//init stack
@12
D=A
@256
M=D

@5
D=A
@257
M=D

//init stack location at RAM[0]
@258
D=A
@SP
M=D

//init LCL
@1015
D=A
@LCL
M=D

//start
@2
D=A //D=2
@LCL
D=M+D //1017 = 1015 + 2
@SP
AM=M-1 //257 = 258-1


D=D+M //1022 = 1017 + 5
A=D-M //A = 1017 = 1022 - 5
D=D-A //D = 5 = 1022 - 1017
M=D //RAM[1017]=5