// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
//This program performs multiplication. It does it by Storing two numbers, one in R0 and one in R1.
//The multiplication is performed by adding R1 to a running total. i and runningtotal both start at 0.
//This happens in the loop by adding runningtotal + R1.
//This loop is performed R0 times, effectively creating a multiplication effect, since R1 is added onto itself R0 times.
//In every iteration of the loop, the loop conditions are checked. If the conditions are no longer met, the program is terminated.
//Before termination, runningtotal is stored in R2.

//Assign RAM[0] to input (row below this)
@4 //input 0 (represents the iteration count)
D=A
@R0
M=D

//Assign RAM[1] to input (row below this)
@1937 //input 1 (represents the amount to add to runningtotal for each iteration)
D=A
@R1
M=D

//Declare RAM[2] (This is done so that R[2] is always 0 at the start of the program execution).
@0
D=A
@R2
M=D

//Declare i (This is done so that i is always 0 at the start of the program execution).
@0
D=A
@i
M=D

//Declare runningtotal (This is done so that runningtotal is always 0 at the start of the program execution).
@0
D=A
@runningtotal
M=D

//Start loop
//while i < R0
(LOOP)
	//Increment running total
	@R1
	D=M
	@runningtotal
	M=D+M
	//Increment iteration
	@i
	M=M+1
	//Check end of loop conditions
	@i
	D=M
	@R0
	D=M-D //Set D to be R0-i.
	@END
	D;JEQ //Go to end if R0-i = 0. JEQ makes the program go to END if D equals 0.
	//Loop when loop conditions are still met
	@LOOP
	0;JMP

(END)
	@runningtotal
	D=M
	@R2
	M=D
	@END
	0;JMP
