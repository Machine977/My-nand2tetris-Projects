(Sys.init)
@0
D=A
@FUNCDEFEND0
D;JEQ
(INCREMENTLCL0)
@SP
M=M+1
A=M-1
M=0
D=D-1
@INCREMENTLCL0
D;JNE
(FUNCDEFEND0)
@4000
D=A
@SP
M=M+1
A=M-1
M=D
@3
D=A
@0
D=D+A
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@5000
D=A
@SP
M=M+1
A=M-1
M=D
@3
D=A
@1
D=D+A
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@Sys.main5
D=A
@SP
A=M
M=D
@LCL
D=M
@SP
AM=M+1
M=D
@ARG
D=M
@SP
AM=M+1
M=D
@THIS
D=M
@SP
AM=M+1
M=D
@THAT
D=M
@SP
AM=M+1
M=D
D=A+1
@SP
M=D
@0
D=A
@5
D=A+D
@SP
A=M-D
D=A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.main
0;JMP
(Sys.main5)
@5
D=A
@1
D=D+A
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
(LOOP)
@LOOP
0;JMP
(Sys.main)
@5
D=A
@FUNCDEFEND9
D;JEQ
(INCREMENTLCL9)
@SP
M=M+1
A=M-1
M=0
D=D-1
@INCREMENTLCL9
D;JNE
(FUNCDEFEND9)
@4001
D=A
@SP
M=M+1
A=M-1
M=D
@3
D=A
@0
D=D+A
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@5001
D=A
@SP
M=M+1
A=M-1
M=D
@3
D=A
@1
D=D+A
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@200
D=A
@SP
M=M+1
A=M-1
M=D
@1
D=A
@LCL
D=M+D
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@40
D=A
@SP
M=M+1
A=M-1
M=D
@2
D=A
@LCL
D=M+D
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@6
D=A
@SP
M=M+1
A=M-1
M=D
@3
D=A
@LCL
D=M+D
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@123
D=A
@SP
M=M+1
A=M-1
M=D
@Sys.add1221
D=A
@SP
A=M
M=D
@LCL
D=M
@SP
AM=M+1
M=D
@ARG
D=M
@SP
AM=M+1
M=D
@THIS
D=M
@SP
AM=M+1
M=D
@THAT
D=M
@SP
AM=M+1
M=D
D=A+1
@SP
M=D
@1
D=A
@5
D=A+D
@SP
A=M-D
D=A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.add12
0;JMP
(Sys.add1221)
@5
D=A
@0
D=D+A
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
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
@LCL
D=M
@1
A=A+D
D=M
@SP
M=M+1
A=M-1
M=D
@LCL
D=M
@2
A=A+D
D=M
@SP
M=M+1
A=M-1
M=D
@LCL
D=M
@3
A=A+D
D=M
@SP
M=M+1
A=M-1
M=D
@LCL
D=M
@4
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
@SP
AM=M-1
D=M
@SP
A=M-1
M=M+D
@SP
AM=M-1
D=M
@SP
A=M-1
M=M+D
@SP
AM=M-1
D=M
@SP
A=M-1
M=M+D
@5
D=A
@LCL
A=M-D
D=M
@R13
M=D
@SP
A=M-1
D=M
@ARG
A=M
M=D
D=A+1
@SP
M=D
@LCL
A=M-1
D=M
@THAT
M=D
@LCL
A=M-1
A=A-1
D=M
@THIS
M=D
@3
D=A
@LCL
A=M-D
D=M
@ARG
M=D
@4
D=A
@LCL
A=M-D
D=M
@LCL
M=D
@R13
D=M
M=0
A=D
0;JMP
(Sys.add12)
@0
D=A
@FUNCDEFEND33
D;JEQ
(INCREMENTLCL33)
@SP
M=M+1
A=M-1
M=0
D=D-1
@INCREMENTLCL33
D;JNE
(FUNCDEFEND33)
@4002
D=A
@SP
M=M+1
A=M-1
M=D
@3
D=A
@0
D=D+A
@SP
AM=M-1
D=D+M
A=D-M
D=D-A
M=D
@5002
D=A
@SP
M=M+1
A=M-1
M=D
@3
D=A
@1
D=D+A
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
@12
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
M=M+D
@5
D=A
@LCL
A=M-D
D=M
@R13
M=D
@SP
A=M-1
D=M
@ARG
A=M
M=D
D=A+1
@SP
M=D
@LCL
A=M-1
D=M
@THAT
M=D
@LCL
A=M-1
A=A-1
D=M
@THIS
M=D
@3
D=A
@LCL
A=M-D
D=M
@ARG
M=D
@4
D=A
@LCL
A=M-D
D=M
@LCL
M=D
@R13
D=M
M=0
A=D
0;JMP
