@0
D=A
@SP
M=M+1
A=M-1
M=D
@0
D=A
@LCL
D=M+D
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
(LOOP_START)
@ARG
D=M
@0
A=A+D
D=M
@SP
M=M+1
A=M-1
M=D
@LCL
D=M
@0
A=A+D
D=M
@SP
M=M+1
A=M-1
M=D
@SP
AM=M-1
D=M
@SP
A=M-1
M=M+D
@0
D=A
@LCL
D=M+D
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@ARG
D=M
@0
A=A+D
D=M
@SP
M=M+1
A=M-1
M=D
@1
D=A
@SP
M=M+1
A=M-1
M=D
@SP
AM=M-1
D=M
@SP
A=M-1
M=M-D
@0
D=A
@ARG
D=M+D
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@ARG
D=M
@0
A=A+D
D=M
@SP
M=M+1
A=M-1
M=D
@SP
AM=M-1
D=M
@LOOP_START  
D;JNE
@LCL
D=M
@0
A=A+D
D=M
@SP
M=M+1
A=M-1
M=D
