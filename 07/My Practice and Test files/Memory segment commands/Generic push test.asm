//init
	//stack segment
	@10
	D=A
	@256
	M=D

	@45
	D=A
	@257
	MD=D
	D=A
	
	@SP
	M=D

	//this segment
	@3010
	D=A
	@THAT
	M=D
	@42
	D=A
	@3012
	M=D
	@45
	D=A
	@3015
	M=D

//Generic push test. push that 5
@THAT //Select Argument
D=M //Save Base Address (to fetch from)
@2 //Select Index
A=A+D //Save Target Address (to fetch from)
D=M //Save target address contents (to fetch from) into D.
@SP //Select Stack
M=M+1 //Increment stack pointer
A=M-1 //Select where stack was pointing, which was *Stack.
M=D //Push the value to where the stack was pointing before the increment.