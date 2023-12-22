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
def ArithCMDProc(line):
    originline = line
    line = line.split()
    command = line[0]
    argument = line[1]
    index = line[2]

    originalargument = argument
    if argument == "local":
        argument = "LCL"
    elif argument == "argument":
        argument = "ARG"
    elif argument == "this":
        argument = "THIS"
    elif argument == "that":
        argument = "THAT"
    elif argument == "temp":
        argument = "temp0"
    elif argument == "static":
        argument = "test." + index
    elif argument == "pointer":
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
            line = "@test.%s\n" % index
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
    if line.startswith("push") or line.startswith("pop") > 0:
        #Run memory segment command.
        line = ArithCMDProc(line) #Feed line into arithmetic command processor.
    elif line in ("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"):
        line = LogicCMDProc(line, linenumber) #Feed line into logic command processor.
    print(line)
    linenumber += 1
    ofile.write(line)

