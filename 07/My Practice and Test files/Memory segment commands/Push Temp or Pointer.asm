



//Push temp/pointer

@index //select index
D=A
@start //select base location
A=D+A //Address to push from = Base location + Index
D=M //Store push value in D
@SP
M=M+1 //Increment stack
A=M-1 //Select previous stack location
M=D //Store value