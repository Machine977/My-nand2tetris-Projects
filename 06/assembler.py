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
        line = line[0:line.find("/")] + "\n"  #replace line with itself without the @, and without anything after the / (comments).

    #Remove spaces.
    line = line.replace(" ", "")
    #Remove \n.
    if line.find("\n") != -1:
        line = line[:len(line)-1]

    return line

#Find labels. Finds labels enclosed in brackets ().
def findlabels(line, linenumber, symboltable):
    #If the line starts with a (, add the contents of the parentheses as a value in the symbol table.
    if line.startswith("(") == True:
#        print(line, linenumber, symboltable)
        symboltable[line[1:len(line)-1]] = symboltable.get(line, linenumber) #Add the second character until the second last character.
#        print(line, linenumber, symboltable)

#Variable parser start. Adds variables to the symbol table if they don't exist, and if they do, converts them to their corresponding location number.
def varparse(line, symboltable, linenumber, basesymlength):
    #First add variables that don't exist in the symbol table.
    if line.startswith("@") == True and line[1] not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"): #Find rows starting with @ and NOT a 0-9 number. We want to identify symbols (variables) such as @i, @test, etc.
        symboltable[line[1:]] = symboltable.get(line[1:], len(symboltable) - basesymlength) #Add variable to the symbol table if it doesn't exist. Ignore the @, and set the base value to be the current length of the symbol table - the base length. E.g if you only have R0-R15, KBD and SCREEN, the base length is 2.
        line = line[0] + str(symboltable[line[1:]])

    return line

#CParser start. Parses C instructions.
def cparser(line):
    line=line.strip() #Remove \n.
    #print("line:", line)


    destination = "" #Set destination variable.
    if line.find("=") != -1:
        destination = line.split("=")[0] #choose the destination part of the line, store it in destination.
        line = line[line.find("=")+1:] #since the destination part is no longer used, trim the line.

    computation = line.split(";")[0] #since the computation part of the line is always used, always create it.

    jump = ""
    if line.find(";") != -1: #run if there's a jump command
        line = line[line.find(";")+1:] #find the jump command, then assign it to the jump variable.
        jump = line


    #print("dest:", destination)
    #print("comp:", computation)
    #print("jump:", jump)

    binstring = "111"
    #Add A/M bit
    if computation.find("M") != -1:
        binstring = binstring+"1"
        computation = computation.replace("M", "A") #Replace M with A, so that it the "computation" part of the string can later be treated the same.
    else:
        binstring = binstring + "0"
    #Add Computation bits
    if computation == "0":
        binstring = binstring + "101010"
    elif computation == "1":
        binstring = binstring + "111111"
    elif computation == "-1":
        binstring = binstring + "111010"
    elif computation == "D":
        binstring = binstring + "001100"
    elif computation == "A":
        binstring = binstring + "110000"
    elif computation == "!D":
        binstring = binstring + "001101"
    elif computation == "!A":
        binstring = binstring + "110001"
    elif computation == "-D":
        binstring = binstring + "001111"
    elif computation == "-A":
        binstring = binstring + "110011"
    elif computation in ("D+1", "1+D"):
        binstring = binstring + "011111"
    elif computation in ("A+1", "1+A"):
        binstring = binstring + "110111"
    elif computation == "D-1":
        binstring = binstring + "001110"
    elif computation == "A-1":
        binstring = binstring + "110010"
    elif computation in ("D+A", "A+D"):
        binstring = binstring + "000010"
    elif computation == "D-A":
        binstring = binstring + "010011"
    elif computation == "A-D":
        binstring = binstring + "000111"
    elif computation in ("D&A", "A&D"):
        binstring = binstring + "000000"
    elif computation in ("D|A", "A|D"):
        binstring = binstring + "010101"

    #Add Destination bits
    if destination.find("A") != -1:
        binstring = binstring + "1"
    else:
        binstring = binstring + "0"

    if destination.find("D") != -1:
        binstring = binstring + "1"
    else:
        binstring = binstring + "0"

    if destination.find("M") != -1:
        binstring = binstring + "1"
    else:
        binstring = binstring + "0"

    #Add Jump bits
    if jump in ("JLT", "JNE", "JLE", "JMP"):
        binstring = binstring + "1"
    else:
        binstring = binstring + "0"

    if jump in ("JEQ", "JGE", "JLE", "JMP"):
        binstring = binstring + "1"
    else:
        binstring = binstring + "0"

    if jump in ("JGT", "JGE", "JNE", "JMP"):
        binstring = binstring + "1"
    else:
        binstring = binstring + "0"

    return binstring

#Main starts here.
inp = input("Please choose file to convert: ") + ".asm"
file = open(inp) #input file
#ofile = open('Hack.hack', 'w') #output file
ofile = open('MyOutput.hack', 'w') #output file

#Initialise symbol table with base values.
symboltable = dict()
registercount = 0 #Add R0-R15.
while registercount < 16:
    symboltable['R%d' % registercount] = registercount #R0 = 0, R1 = 1, etc. Up to and including 15.
    registercount += 1
symboltable['SCREEN'] = 16384 #Add remaining base variables to symbol table.
symboltable['KBD'] = 24576
#Add weird symbols, specified by Nand2Tetris. Not used in my test program however.
symboltable["SP"] = 0
symboltable["LCL"] = 1
symboltable["ARG"] = 2
symboltable["THIS"] = 3
symboltable["THAT"] = 4

linenumber = 0
#Run through the file the first time. While doing this, load the desired lines into a list, since we want to traverse through the file more than once (can't do so otherwise without opening it twice).
mlist = list()
for line in file:
    #Clean lines, we only want to look at lines with actual code of some sort (or symbols).
    line = lineclean(line)
    if line == "": #If the line has nothing worth parsing, go to the next line.
        continue

    #Find the labels contained in () and add them to the symbol table.
    findlabels(line, linenumber, symboltable)

    #Only add to the linenumber counter and append to the list if the line isn't a label. Labels don't count as lines in the file and we need only parse them just this once to remember what line they're on.
    if line.startswith("(") == False: #Don't increment line count for lines starting with ( since they don't count.
        linenumber += 1
        mlist.append(line)

#Debug code block
#linenumber = 0
#for line in mlist:
#    print(linenumber, line)
#    linenumber += 1
#print(symboltable)

#Set base symbol table length.
basesymlength = len(symboltable) - 16 #Declare the base length of the symbol table. This is the standard symbols (R0-R15 + KBD + SCREEN), plus all the labels in the file. This is later used in variable creation (varparse). This is minused by 16 since the first 16 variables are reserved for R0-R15.

linenumber = 0

#Run through the file the second time. This time, identify whether the instruction is a or c and convert it to binary. If it's an a instruction, check that it's in a number format (if not, convert it).
for line in mlist:
    #a instruction
    if line[0] == "@":
        line = varparse(line, symboltable, linenumber, basesymlength) #Will convert variables to their register number equivalents, and leave non-variables (e.g @54) untouched.
        line = bin(int(line[1:]))[2:] #Convert all characters in line except the @ into binary, then get rid of the "0b" that binary in python starts with.
        while len(line) < 16: #Add zeroes to the start of the binary number, so that there are zeroes before the first 1 and it's always 16 characters long.
            line = "0" + line
    #c instruction
    else:
        line = cparser(line)
    line = line + "\n"
    print(line, end="")
    ofile.write(line)

