import os

def lineclean(line):
    #Strip whitespace on both sides (tabs, spaces, etc)
    line = line.strip()

    #Remove // comment
    x = line.find("//")
    if x != -1:
        line = line[:x]

    #Remove /** comment.
    x = line.find("/**")
    if x != -1:
        line = line[:x]

    return line

def tokeniser(file, symbol, keyword, numbers):
    blockcommentflag = 0
    file = open(file)
    wlist = list() #Create word list for this file.
    for line in file:
        #Handle block comments
        if line.find("/**") != -1 and line.find("*/") != -1: #If a block comment starts and ends on the same row, get rid of it.
            line = line[:line.find("/**")]
        elif line.find("/**") != -1: #If a block comment starts on a row, ignore all following rows until it ends.
            blockcommentflag = 1
        if line.find("*/") != -1: #If a block comment has ended, start reading again.
            blockcommentflag = 0
            line = line[line.find("*/") + 2:]

        #Clean lines, ignore empty/commented out lines.
        line = lineclean(line)
        if line == "" or blockcommentflag == 1:
            continue


#        wlist = list()
        word = ""
        flag = 1

        for letter in line:
            if flag == 1: #If the letter is not part of a string.

                if letter.isalpha() == True or letter.isnumeric() == True: #If the letter is a-z or 0-9 and flag is 1 (i.e word is not part of a string), concatenate it into a word.
                    word = word + letter
                elif letter.isalpha() == False and letter.isnumeric() == False and len(word) > 0: #Append the word to the list when it's ended.
                    wlist.append(word)
                    word = ""

                if letter == '"': #Prepare to handle string
                    flag = 0
                    word = '"'
                elif letter in symbol:
                    wlist.append(letter)

            else: #If the letter is part of a string.
                if letter == '"': #Once the end of the string is reached, set flag back to 1.
                    flag = 1
                    wlist.append(word)
                    word = ""
                else:
                    word = word + letter
    return wlist

def writeTokensToXML(wlist, ofile, symbol, keyword, numbers):
    ofile.write("<tokens>\n")
    for word in wlist:
        if word in symbol:
            #<, >, and & are special cases. These interfere with html or something so should be replaced with the values below.
            if word == "<":
                word = "&lt;"
            elif word == ">":
                word = "&gt;"
            elif word == "&":
                word = "&amp;"
            ofile.write("<symbol> " + word + " </symbol>\n")
        elif word in keyword:
            ofile.write("<keyword> " + word + " </keyword>\n")
        elif word.startswith('"') == True:
            ofile.write("<stringConstant> " + word[1:] + " </stringConstant>\n")
        elif word.startswith(numbers):
            ofile.write("<integerConstant> " + word + " </integerConstant>\n")
        else:
            ofile.write("<identifier> " + word + " </identifier>\n")
    ofile.write("</tokens>\n")




def getTokenType(item):

    #Check if the first tag and the last tag match, and that they have a space.
    if item[:item.find(">") + 2] == "<keyword> " and item[item.find("</")-1:] == " </keyword>":
        return "keyword"
    elif item[:item.find(">") + 2] == "<identifier> " and item[item.find("</")-1:] == " </identifier>":
        return "identifier"
    elif item[:item.find(">") + 2] == "<symbol> " and item[item.find("</")-1:] == " </symbol>":
        return "symbol"
    elif item[:item.find(">") + 2] == "<integerConstant> " and item[item.find("</")-1:] == " </integerConstant>":
        return "integerConstant"
    elif item[:item.find(">") + 2] == "<stringConstant> " and item[item.find("</")-1:] == " </stringConstant>":
        return "stringConstant"
    else:
        return "invalid"

def getToken(item):
    return item[item.find(">") + 2:item.find("</") - 1]

def classmethod(indent, itemcounter, fileLineList, ofile):
    #Write class tag
    ofile.write("<class>\n")

    #Create indent.
    indent += "  "

    #Write starting keyword (<keyword> class </keyword>)
    ofile.write(indent + fileLineList[itemcounter] + "\n")

    #Move to next item.
    itemcounter += 1

    #Check if next item is an identifier with the class name.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: Class keyword is not followed by an identifier token.")

    #Check if next item is a {
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: Class name keyword is not followed by a { token.")

    #Check if next item is a classVarDec (optional).
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "keyword" and (token == "static" or token == "field"):
        classVarDec(indent, itemcounter, fileLineList, ofile)

    print(tokentype, token)

    #Check if next item is a subroutineDec (optional).
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "keyword" and (token == "constructor" or token == "function" or token == "method"):
        subroutineDec(indent, itemcounter, fileLineList, ofile)


    #Write class end tag
    ofile.write("</class>\n")

def classVarDec(indent, itemcounter, fileLineList, ofile):
    print("classVarDec success!")

def subroutineDec(indent, itemcounter, fileLineList, ofile):
    print("subroutineDec success!")
    #Write subroutineDec tag.
    ofile.write(indent + "<subroutineDec>\n")
    indent += "  "

    #Write starting keyword (constructor, method, or function)
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    ofile.write(indent + fileLineList[itemcounter] + "\n")

    #Move to next item.
    itemcounter += 1

    #Check if next item is a "type": either void, int, char, boolean, or a className. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    typeflag = type(tokentype, token)
    if typeflag == 1:
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: subroutine return variable not declared!")

    #Check if next item is a subroutine name or not. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: subroutine name not declared!")

    #Check if next item is a (. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "(":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: subroutine definition start ( is not present!")

    #Check if next item is a parameter list. Obligatory, but actual content is optional.
    parameterList(indent, itemcounter, fileLineList, ofile)

    #Check if next item is a ). Obligatory
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ")":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: subroutine definition end ) is not present!")

    #Check if next item is a subroutineBody. Obligatory.
    subroutineBody(indent, itemcounter, fileLineList, ofile)

    #Write subroutineDec end tag.
    indent = indent[:len(indent)-2]
    ofile.write(indent + "</subroutineDec>\n")

def parameterList(indent, itemcounter, fileLineList, ofile):
    print("parameterList success")

    ofile.write(indent + "<parameterList>\n")

    ofile.write(indent + "</parameterList>\n")

def subroutineBody(indent, itemcounter, fileLineList, ofile):
    #Write subroutineBody start tag.
    ofile.write(indent + "<subroutineBody>\n")
    indent += "  "

    #Check if next character is a {. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: subroutine body start { is not present!")

    #Check if next character is a variable declaration. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "keyword" and token == "var":
        varDec(indent, itemcounter, fileLineList, ofile)

    #Write subroutineBody end tag.
    indent = indent[:len(indent)-2]
    ofile.write(indent + "</subroutineBody>\n")

def varDec(indent, itemcounter, fileLineList, ofile):
    ofile.write(indent + "<varDec>\n")
    indent += "  "

    #Write var token.
    ofile.write(indent + fileLineList[itemcounter] + "\n")
    itemcounter += 1

    #Check if next token is a "type". Obligatory
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    typeflag = type(tokentype, token)
    #start again here
    if typeflag == 1:
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: variable type not specified!")

    #Check if next token is an identifier. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: variable name not specified!")

    #Check if next token is a ;. Obligatory
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: variable declaration does not end with a ;.")


#    token = ""
#    while token != ";":

#        tokentype = getTokenType(fileLineList[itemcounter])
#        token = getToken(fileLineList[itemcounter])

    print(fileLineList[itemcounter])


    indent = indent[:len(indent)-2]
    ofile.write(indent + "</varDec>\n")




def type(tokentype, token):
    #This function checks if the token is of the type "type".
    if (tokentype == "keyword" and token in ("void", "int", "char", "boolean")) or tokentype == "identifier":
        return 1
    else:
        return 0


#Main starts here.
symbol = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"] #Define symbols
keyword = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"] #Define keywords

#Find all vm files in directory and open them.
filelist = list()
for mfile in os.listdir():
    if mfile.endswith(".jack") == True:
        filelist.append(mfile)
print(filelist)


numbers = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
for file in filelist:
    #Create name for output file.
    outfilename = file.replace(".jack", "T.xml")
    ofile = open(outfilename, 'w') #output file

#Tokeniser
    #Return a list of tokens for the current file.
    wlist = tokeniser(file, symbol, keyword, numbers)

    #Take word list in the current file and use it to generate some xml.
    writeTokensToXML(wlist, ofile, symbol, keyword, numbers)

    ofile.close()


#Jack Analyzer
filelist = list()
for mfile in os.listdir():
    if mfile.endswith("T.xml") == True:
        filelist.append(mfile)
print(filelist)





#store the whole token file in a list.
fileLineList = list()
for file in filelist:

    print(file)
    #Create name for output file.
    outfilename = file.replace("T.xml", ".xml")
    ofile = open(outfilename, 'w') #output file

    #Add each line in file to a list for analysis.
    file = open(file)
    for line in file:
        fileLineList.append(line[:len(line)-1]) #Don't include \n.
    file.close()

    #Delete first and last <tokens> and </tokens> tags.
    del fileLineList[0]
    del fileLineList[len(fileLineList)-1]

    indent = ""
    itemcounter = 0
    for item in fileLineList:
        tokentype = getTokenType(item)
        token = getToken(item)
        if tokentype == "keyword" and token == "class":
            classmethod(indent, itemcounter, fileLineList, ofile)

        itemcounter += 1

    ofile.close()




#Create a function that contains all types of XML tags, and make it recursively run.


#print(wlist)
