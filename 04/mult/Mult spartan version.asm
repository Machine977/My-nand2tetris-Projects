@4 //input 0
D=A
@0 //Register 0, but no R0 this time.
M=D
@1937 //input 2
D=A
@1 //Register 1, but no R1 this time.
M=D
@0
D=A
@2
M=D //Register 2, but no R2 this time.
@0
D=A
@16 //Variable i, but now it's just register 16 instead (program runs exactly the same).
M=D
@0
D=A
@17 //Variable runningtotal, but now it's just register 16 instead (program runs exactly the same).
M=D
	@1
	D=M
	@17
	M=D+M
	@16
	M=M+1
	@16
	D=M
	@0
	D=M-D
	@34
	D;JEQ
	@20
	0;JMP
@17
D=M
@2
M=D
@34
0;JMP

//Note that since notepad starts on row 1, telling the program to jump to instruction 30 (e.g row 31), one has
//to refer to the instruction number minus 1.