//init stack
@25
D=A
@256
M=D

@50
D=A
@257
M=D

@75
D=A
@258
M=D

@259
D=A
@SP
M=D

//Stack pointer starts at 259. 256, 257, and 258 contain 25, 50, and 75 respectively.

//Pop static test
@SP //Select stack
AM=M-1 //Decrement stack, find top value.
D=M //Store top value
@test.5 //Find location to store
M=D


//testing
//@SP //Select stack
//AM=M-1 //Decrement stack, find top value.
//D=M //Store top value
//@test.2 //Find location to store
//M=D