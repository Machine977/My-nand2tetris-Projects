//Pointer pop test
@257
D=A
@SP
M=D

@3030
D=A
@SP
A=M-1
M=D


//Pop Temp
@5 //Get 5 (Temp0 starts at register 5)
D=A
@2 //replace 2 with the index.
D=D+A //Choose base register location to pop to.
@SP //choose stack.
AM=M-1 //decrement stack whilst saving pop value, select the stack pointer's new register.


D=D+M // Get total (register to pop to + pop value).
A=D-M //Select register to pop to (Total - pop value)
D=D-A //Store pop value (total - register to pop to)
M=D //Store value in selected register.