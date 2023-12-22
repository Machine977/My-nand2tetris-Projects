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
    line = line.replace(" ", "") #Remove spaces.
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
    functionname = line[1]

    #//Function definition. Initialise local variables to 0, then increment stack pointer by local variable count.
    #Declare start of function
    line = "(%s)\n" % functionname

    #Allocate local variables.
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

    #print(line)
    return line

def returnconv(line):
    #Get return address, store it in R13. Note that this must be done before popping the stack into ARG[0], since if the function had 0 arguments the address will be overwritten. (The address will be located in the same spot as ARG[0], since there are no arguments).
    line = "@5\n"
    line += "D=A\n"
    line += "@LCL\n"
    line += "A=M-D\n"
    line += "D=M\n"
    line += "@R13\n"
    line += "M=D\n"
    #Pop the stack, put it into ARG[0] and set the stack pointer to ARG[0]+1.
    line += "@SP\n"
    line += "A=M-1\n"
    line += "D=M\n"
    line += "@ARG\n"
    line += "A=M\n"
    line += "M=D\n"
    line += "D=A+1\n"
    line += "@SP\n"
    line += "M=D\n"
   #Restore THAT (LCL - 1)
    line += "@LCL\n"
    line += "A=M-1\n"
    line += "D=M\n"
    line += "@THAT\n"
    line += "M=D\n"
    #Restore THIS (LCL - 2)
    line += "@LCL\n"
    line += "A=M-1\n"
    line += "A=A-1\n"
    line += "D=M\n"
    line += "@THIS\n"
    line += "M=D\n"
    #Restore ARG (LCL - 3)
    line += "@3\n"
    line += "D=A\n"
    line += "@LCL\n"
    line += "A=M-D\n"
    line += "D=M\n"
    line += "@ARG\n"
    line += "M=D\n"
    #Restore LCL (LCL - 4)
    line += "@4\n"
    line += "D=A\n"
    line += "@LCL\n"
    line += "A=M-D\n"
    line += "D=M\n"
    line += "@LCL\n"
    line += "M=D\n"
    #Return to next instruction.
    line += "@R13\n"
    line += "D=M\n"
    line += "M=0\n" #Set R13 to be 0 again.
    line += "A=D\n"
    line += "0;JMP\n"
    return line

def callconv(callstring, linenumber):
    callstring = callstring.split()
    functionname = callstring[1]
    argumentcount = callstring[2]

    #Save return address.
    line = "@%s%s\n" % (functionname, linenumber)
    line += "D=A\n"
    line += "@SP\n"
    line += "A=M\n"
    line += "M=D\n"
    #Backup LCL
    line += "@LCL\n"
    line += "D=M\n"
    line += "@SP\n"
    line += "AM=M+1\n"
    line += "M=D\n"
    #Backup ARG
    line += "@ARG\n"
    line += "D=M\n"
    line += "@SP\n"
    line += "AM=M+1\n"
    line += "M=D\n"
    #Backup THIS
    line += "@THIS\n"
    line += "D=M\n"
    line += "@SP\n"
    line += "AM=M+1\n"
    line += "M=D\n"
    #Backup THAT
    line += "@THAT\n"
    line += "D=M\n"
    line += "@SP\n"
    line += "AM=M+1\n"
    line += "M=D\n"
    #Increment stack pointer to point at new LCL 0.
    line += "D=A+1\n"
    line += "@SP\n"
    line += "M=D\n"
    #Set new ARG.
    line += "@%s\n" % argumentcount
    line += "D=A\n"
    line += "@5\n"
    line += "D=A+D\n"
    line += "@SP\n"
    line += "A=M-D\n"
    line += "D=A\n"
    line += "@ARG\n"
    line += "M=D\n"
    #Update LCL so that it points to where the stack pointer currently is (just below where the old THAT is saved).
    line += "@SP\n"
    line += "D=M\n"
    line += "@LCL\n"
    line += "M=D\n"
    #Go to actual function, now that setup is done.
    line += "@%s\n" % functionname
    line += "0;JMP\n"
    #Return here once the function is over.
    line += "(%s%s)\n" % (functionname, linenumber)

    return line

def lineparser(line):
    print(line)
    global linenumber
    #Line is a push or pop.
    if line.startswith("push") or line.startswith("pop") > 0:
        #Run memory segment command.
        line = ArithCMDProc(line, inp) #Feed line into arithmetic command processor.

    #Line is an arithmetic/logic operation.
    elif line.startswith(("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not")):
        line = LogicCMDProc(line, linenumber) #Feed line into logic command processor.

    #Line is a label.
    elif line.startswith("label"):
        line = line.split()
        line = "(" + line[1] +")\n"

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
        line = callconv(line, linenumber)

    #print(linenumber)
    linenumber += 1
    print(line)
    return line


#Main starts here.


inp = input("Please choose file to convert: ")
inpfilename = inp + ".vm"
mainfile = open(inpfilename) #input file
outfilename = inp + ".asm"
ofile = open(outfilename, 'w') #output file

#Find all vm files in directory that were not specified and open them. We want the functions at the top of our file.
filelist = list()
for mfile in os.listdir():
    if mfile.endswith(".vm") == True and mfile != inpfilename:
        filelist.append(mfile)
print(filelist)


#Run through the main file the first time. While doing this, load the desired lines into a list, since we want to traverse through the file more than once (can't do so otherwise without opening it twice).
mlist = list()
linenumber = 0

#Boot the file. Set SP = 256, and call sys.init.
bootstring = "@256\nD=A\n@SP\nM=D\n" #Set the stack pointer to 256, since this is difficult (if not impossible?) using VM commands.
ofile.write(bootstring)
mlist.append("call Sys.init 0") #This line will get parsed (and therefore translated) by the parser.

for line in mainfile:
    #Clean lines, we only want to look at lines with actual code of some sort 
    line = lineclean(line)
    if line == "": #If the line has nothing worth parsing, go to the next line.
        continue
    mlist.append(line)
#print(mlist)

for file in filelist:
    file = open(file)
    for line in file:
        line = lineclean(line)
        if line == "":
            continue
        mlist.append(line)
#for element in mlist:
    #print(element)

#mlist now contains all the files, with the input file at the top.
#Run through the file the second time. This time, actually parse each line and create some code.
for line in mlist:
    line = lineparser(line)

    #print(line)
    ofile.write(line)

