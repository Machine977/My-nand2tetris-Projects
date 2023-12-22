// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

//This program flips all the bits in the matrix to turn on while the user inputs a keystroke.
//The register set is 16384 to 24575. This is equal to 8192 registers (16384 is register 0, 24575 is register 8191).
//Think 1-3 has only one number in between it (2), but there's a gap of two numbers (1 to 2, 2 to 3, 3-1=2).
//So counting 1 as 1, 2 as 2, but not 3 as 3 means we have 2 numbers in between 1 and 3.
//Register 24576 (final register) is reserved for the keyboard input and does not affect the screen, unlike 16384 <-> 24575.

(START)
@10
D=A
@5
AMD=D
M=1