////init
////init stack base
//@260
//D=A
//@SP
//M=D
//
////init stack itself
//@256
//M=A
//@257
//M=A
//@258
//M=A
//@259
//M=A

//Add command
@SP
AM=M-1 //Select top value, decrement stack.
D=M //Store top value in D
@SP
A=M-1 //Select bottom value location
M=M+D //New bottom value = bottom value + top value