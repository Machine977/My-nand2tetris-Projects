import os

#Clean line. Clears the line so it's ready for processing.
def lineclean(line):
    #Remove tabs and spaces at the start of the line
    while line.startswith(("\t", " ")) == True:
        line = line.replace("\t", "")
        line = line.replace(" ", "")

    #Remove empty lines and lines with comments. Note that these get replaced with empty lines, that is two quotation marks "", so they're not really gone.
    if line.startswith(("//", "\n")) == True:
        line = ""

    #Remove comments at the end of the line.
    if line.find("//") != -1:
        line = line[:line.find("/")] #replace line with itself without anything after the / (comments).

    #Remove \n.
    if line.find("\n") != -1:
        line = line[:len(line)-1]

    return line

#Arithmetic command processor
def ArithCMDProc(line, filename):
    originline = line
    line = line.split()
    command = line[0]
    argument = line[1]
    index = line[2]

    originalargument = argument
    if originalargument == "local":
        argument = "LCL"
    elif originalargument == "argument":
        argument = "ARG"
    elif originalargument == "this":
        argument = "THIS"
    elif originalargument == "that":
        argument = "THAT"
    elif originalargument == "temp":
        argument = "temp0"
    elif originalargument == "static":
        argument = "%s." % filename + index
    elif originalargument == "pointer":
        argument = "THIS"

#Get location for temp/pointer registers.
    if originalargument == "temp":
        start = "5" #temp
    else:
        start = "3" #pointer

#push operation
    if command == "push":
        if originalargument in ("local", "argument", "this", "that"):
            line = "@%s\n" % argument
            line += "D=M\n"
            line += "@%s\n" % index
            line += "A=A+D\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "M=M+1\n"
            line += "A=M-1\n"
            line += "M=D\n"
        elif originalargument == "constant":
            line = "@%s\n" % index
            line += "D=A\n"
            line += "@SP\n"
            line += "M=M+1\n"
            line += "A=M-1\n"
            line += "M=D\n"
        elif originalargument in ("temp", "pointer"):
            line = "@%s\n" % start
            line += "D=A\n"
            line += "@%s\n" % index
            line += "A=A+D\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "M=M+1\n"
            line += "A=M-1\n"
            line += "M=D\n"
        elif originalargument == "static":
            line = "@%s.%s\n" % (filename, index)
            line += "D=M\n"
            line += "@SP\n"
            line += "M=M+1\n"
            line += "A=M-1\n"
            line += "M=D\n"

#pop operation
    else:
        if originalargument in ("local", "argument", "this", "that"):
            line = "@%s\n" % index
            line += "D=A\n"
            line += "@%s\n" % argument
            line += "D=M+D\n"
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=D+M\n"
            line += "A=D-M\n"
            line += "D=D-A\n"
            line += "M=D\n"
        elif originalargument in ("temp", "pointer"):
            line = "@%s\n" % start
            line += "D=A\n"
            line += "@%s\n" % index
            line += "D=D+A\n"
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=D+M\n"
            line += "A=D-M\n"
            line += "D=D-A\n"
            line += "M=D\n"
        elif originalargument == "static":
            line = "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@%s\n" % argument
            line += "M=D\n"
    return line

#Logic command processor
def LogicCMDProc(line, linenumber):
    originline = line
    if line == "add":
        line = "@SP\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=M+D\n"
    elif line == "sub":
        line = "@SP\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=M-D\n"
    elif line == "neg":
        line = "@SP\n"
        line += "A=M-1\n"
        line += "M=-M\n"
    elif line == "eq":
        line = "@SP\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "D=M-D\n"
        line += "@TRUE%s\n" % linenumber
        line += "D;JEQ\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=0\n"
        line += "@END%s\n" % linenumber
        line += "0;JMP\n"
        line += "(TRUE%s)\n" % linenumber
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=-1\n"
        line += "(END%s)\n" % linenumber
    elif line == "gt":
        line = "@SP\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "D=M-D\n"
        line += "@TRUE%s\n" % linenumber
        line += "D;JGT\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=0\n"
        line += "@END%s\n" % linenumber
        line += "0;JMP\n"
        line += "(TRUE%s)\n" % linenumber
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=-1\n"
        line += "(END%s)\n" % linenumber
    elif line == "lt":
        line = "@SP\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "D=M-D\n"
        line += "@TRUE%s\n" % linenumber
        line += "D;JLT\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=0\n"
        line += "@END%s\n" % linenumber
        line += "0;JMP\n"
        line += "(TRUE%s)\n" % linenumber
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=-1\n"
        line += "(END%s)\n" % linenumber
    elif line == "and":
        line = "@SP\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=M&D\n"
    elif line == "or":
        line = "@SP\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M-1\n"
        line += "M=M|D\n"
    elif line == "not":
        line = "@SP\n"
        line += "A=M-1\n"
        line += "M=!M\n"
    return line

def functionconv(line, linenumber):
    originalline = line
    line = line.split()
    localvariablecount = line[2]

    #//Function definition. Initialise local variables to 0, then increment stack pointer by local variable count.
    line = "@SP\n"
    line += "D=M\n"
    line += "@LCL\n"
    line += "M=D\n"
    line += "@%s\n" % localvariablecount #Get variable count
    line += "D=A\n"
    line += "@FUNCDEFEND%s\n" % linenumber #If variable counter = 0, go to end of function definition.
    line += "D;JEQ\n"
    line += "(INCREMENTLCL%s)\n" % linenumber #Initialise local variable to 0, increase stack pointer.
    line += "@SP\n"
    line += "M=M+1\n"
    line += "A=M-1\n"
    line += "M=0\n"
    line += "D=D-1\n"
    line += "@INCREMENTLCL%s\n" % linenumber #If remaining local variable count >0, do it again. Repeat until all local variables have been initialised (count is 0).
    line += "D;JNE\n"
    line += "(FUNCDEFEND%s)\n" % linenumber #End the function definition.

    print(line)
    return line

def returnconv(line):
    line = "@SP\n"
    line += "A=M-1\n"
    line += "D=M\n"
    line += "@ARG\n"
    line += "A=M\n"
    line += "M=D\n"
    line += "D=A+1\n"
    line += "@SP\n"
    line += "M=D\n"
    line += "@LCL\n"
    line += "A=M-1\n"
    line += "D=M\n"
    line += "@THAT\n"
    line += "M=D\n"
    line += "@LCL\n"
    line += "A=M-1\n"
    line += "A=A-1\n"
    line += "D=M\n"
    line += "@THIS\n"
    line += "M=D\n"
    line += "@3\n"
    line += "D=A\n"
    line += "@LCL\n"
    line += "A=M-D\n"
    line += "D=M\n"
    line += "@ARG\n"
    line += "M=D\n"
    line += "@4\n"
    line += "D=A\n"
    line += "@LCL\n"
    line += "A=M-D\n"
    line += "D=M\n"
    line += "@LCL\n"
    line += "M=D\n"
    return line



#Main starts here.
inp = input("Please choose file to convert: ")
inpfilename = inp + ".vm"
file = open(inpfilename) #input file
outfilename = inp + ".asm"
ofile = open(outfilename, 'w') #output file

#Run through the file the first time. While doing this, load the desired lines into a list, since we want to traverse through the file more than once (can't do so otherwise without opening it twice).
mlist = list()
linenumber = 0
for line in file:
    #Clean lines, we only want to look at lines with actual code of some sort 
    line = lineclean(line)
    if line == "": #If the line has nothing worth parsing, go to the next line.
        continue
    mlist.append(line)

#Run through the file the second time. This time, actually parse each line and create some code.
for line in mlist:
    print(line)
    #Line is a push or pop.
    if line.startswith("push") or line.startswith("pop") > 0:
        #Run memory segment command.
        line = ArithCMDProc(line, inp) #Feed line into arithmetic command processor.

    #Line is an arithmetic/logic operation.
    elif line in ("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"):
        line = LogicCMDProc(line, linenumber) #Feed line into logic command processor.

    #Line is a label.
    elif line.startswith("label"):
        line = "(" + line[6:] +")\n"

    #Line is a goto.
    elif line.startswith("goto"):
        line = "@" + line[5:] + "\n0;JMP\n"
    #Line is an if-goto. Check the stack pointer, if it's true then go.
    elif line.startswith("if-goto"):
        line = "@SP\nAM=M-1\nD=M\n@" + line[8:] + "\nD;JNE\n" #As far as the if-goto command is concerned, the stack value is true if it is anything other than 0. So if the contents of the stack pointer is not 0, do the goto (and decrement the stack).

    #Line is a function.
    elif line.startswith("function"):
        line = functionconv(line, linenumber)

    elif line.startswith("return"):
        line = returnconv(line)

    elif line.startswith("call"):
        line = callconv(line)

    #print(line)
    linenumber += 1
    ofile.write(line)

