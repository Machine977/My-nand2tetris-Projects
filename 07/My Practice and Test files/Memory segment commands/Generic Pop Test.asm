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

//Init THIS to be 3030
@3030
D=A
@3
M=D

//Init THAT to be 3040
@3040
D=A
@4
M=D

//Generic pop

//@i //replace i with the index.
//D=A //D=i
//@LCL //replace LCL with base register location to pop to.
//D=M+D //1017 = 1015 + 2
//@SP //decrement stack.
//AM=M-1 //257 = 258-1
//
//
//D=D+M //1022 = 1017 + 5
//A=D-M //A = 1017 = 1022 - 5
//D=D-A //D = 5 = 1022 - 1017
//M=D //RAM[1017]=5


//testing:
//pop that 5

@5 //replace 5 with the index.
D=A //Store Index
@THAT //Choose base register location to pop to. Doesn't have to be THAT.
D=M+D //Find register to pop to (index + base location).
@SP //choose stack.
AM=M-1 //decrement stack whilst saving pop value, select the stack pointer's new register.


D=D+M // Get total (register to pop to + pop value).
A=D-M //Select register to pop to (Total - pop value)
D=D-A //Store pop value (total - register to pop to)
M=D //Store value in selected register.