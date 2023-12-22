import os

#Tokeniser functions.
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


#########################################################################################################################################################################

#Parser functions.

#Finds the token type.
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

#Fetches the actual token.
def getToken(item):
    return item[item.find(">") + 2:item.find("</") - 1]

def classmethod(indent, itemcounter, fileLineList, ofile):

    #Move to next item.
    itemcounter += 1

    #Check if next item is an identifier with the class name.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    className = token
    if tokentype == "identifier":
        dummySymboltable = dict() #Symbol table for the class doesn't need to exist until fields start getting declared.
        category = "Class"
        role = "Defined"
        itemcounter = identifier(indent, itemcounter, fileLineList, ofile, dummySymboltable, category, role, token)
    else:
        ofile.write("Error: Class keyword is not followed by an identifier token.")

    #Check if next item is a {. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        itemcounter += 1
    else:
        ofile.write("Error: Class name keyword is not followed by a { token.")

    #Check if next item is a classVarDec (optional). Once finished, repeat again if the current token is still a classVarDec.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    classSymbolTable = dict()
    while tokentype == "keyword" and (token == "static" or token == "field"):
        itemcounter = classVarDec(indent, itemcounter, fileLineList, ofile, classSymbolTable)
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
    print("classSymbolTable=", classSymbolTable)

    #Check if next item is a subroutineDec (optional). Once finished, repeat again if the current token is still a subroutineDec.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "keyword" and (token == "constructor" or token == "function" or token == "method"):
        ##### Only for illustrative purposes, not used for translation.
        subrType = token
        subrName = getToken(fileLineList[itemcounter+2])
        ##### Only for illustrative purposes, not used for translation.

        subrSymbolTable = dict()

        ofile.write("function " + className + ".") #Define function. Subroutine name and local var count come after this.

        itemcounter = subroutineDec(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className)
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        #Illustrative purposes.
        print("subrSymbolTable for", subrType, subrName, "=", subrSymbolTable)


    #Check if next item is a }. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "}":
        itemcounter += 1
    else:
        ofile.write("Error: Class content is not followed by a } token.")

    return itemcounter

def classVarDec(indent, itemcounter, fileLineList, ofile, classSymbolTable):

    #Write static/field token.
    kind = getToken(fileLineList[itemcounter]) #Save whether it's a field or a static.
    itemcounter += 1

    #Check if current token is a "type": either int, char, boolean, or a className. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    mtype = token
    typeflag = jacktype(tokentype, token)
    if typeflag == 1:
        #If it's an identifier, put it under a new tag.
        if tokentype == "identifier":
            category = "Class"
            role = "Used"
            itemcounter = identifier(indent, itemcounter, fileLineList, ofile, classSymbolTable, category, role, token)
        #If it's not an identifier, do not indent. Add the token.
        else:
            itemcounter += 1
    else:
        ofile.write("Error: Class variable (field) type not declared!")

    #Check if current token is an identifier (varName). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":
        AddToSymbolTable(token, mtype, kind, classSymbolTable) #Add the token, type, and kind to the symbol table.
        category = kind #either field or static.
        role = "Defined"
        itemcounter = identifier(indent, itemcounter, fileLineList, ofile, classSymbolTable, category, role, token)

    else:
        print("Error: variable name not specified!")

    #Check if current token is a ,. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "symbol" and token == ",":
        itemcounter += 1

        #Check if current token is an identifier (varName). Obligatory if preceded by a ,.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype == "identifier":
            AddToSymbolTable(token, mtype, kind, classSymbolTable) #Add the token, type, and kind to the symbol table.
            category = kind #either field or static.
            role = "Defined"
            itemcounter = identifier(indent, itemcounter, fileLineList, ofile, classSymbolTable, category, role, token)
        else:
            print("Error: Class variable (field) name not specified after comma!")
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])

    #Check if current token is a ;. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        itemcounter += 1
    else:
        print("Error: variable name not specified!")

    return itemcounter

def subroutineDec(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className):

    #Write starting keyword (constructor, method, or function)
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    subroutineType = token


    #Move to next item.
    itemcounter += 1


    #Check if next item is a "type": either void, int, char, boolean, or a className. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    typeflag = jacktype(tokentype, token)
    if typeflag == 1 or (tokentype == "keyword" and token == "void"):
        #Check if the subroutine is void or not. Save this for return statements later.
        if token == "void":
            voidFlag = True
        else:
            voidFlag = False

        #If it's an identifier, put it under a new tag.
        if tokentype == "identifier":
            category = "Class"
            role = "Used"
            itemcounter = identifier(indent, itemcounter, fileLineList, ofile, subrSymbolTable, category, role, token)
        #If it's not an identifier, do not indent. Add the token.
        else:
            itemcounter += 1
    else:
        ofile.write("Error: subroutine return variable not declared!")

    #Check if next item is a subroutine name or not. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":
        dummySymboltable = dict() #Symbol table for the subroutine doesn't need to exist until fields start getting declared.
        category = "Subroutine"
        role = "Defined"
        itemcounter = identifier(indent, itemcounter, fileLineList, ofile, dummySymboltable, category, role, token)

        #Save subroutineName for function definition.
        subroutineName = token

    else:
        ofile.write("Error: subroutine name not declared!")

    #Check if next item is a (. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "(":
        itemcounter += 1
    else:
        ofile.write("Error: subroutine definition start ( is not present!")

    #Check if next item is a parameter list. Obligatory, but actual content is optional.
    itemcounter = parameterList(indent, itemcounter, fileLineList, ofile, subrSymbolTable)

    #Check if next item is a ). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ")":
        itemcounter += 1
    else:
        ofile.write("Error: subroutine definition end ) is not present!")

    #Write function definition.
    ofile.write(subroutineName + " ")

    #If the subroutine is a constructor, remember this. After the variable declaration but before the statements, initialise the object.
    if subroutineType == "constructor":
        constructorFlag = True #Remember if the subroutine is a constructor or not. If it is, return "this". In VM, just before the return, "push pointer 0".
        #AddToSymbolTable("this", "argument", subrSymbolTable)
    else:
        constructorFlag = False

    #If the subroutine is a method, start by selecting the object. Argument 0 will be the object's base address.
    if subroutineType == "method":
        methodFlag = True
    else:
        methodFlag = False


    #Check if next item is a subroutineBody. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        itemcounter = subroutineBody(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, constructorFlag, methodFlag, className)
    else:
        ofile.write("Error: subroutineBody doesn't start with a {!")

    return itemcounter

def parameterList(indent, itemcounter, fileLineList, ofile, subrSymbolTable):

    #Check if current token is a "type": either int, char, boolean, or a className. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    mtype = token
    typeflag = jacktype(tokentype, token)
    if typeflag == 1:
        #If it's an identifier, put it under a new tag.
        if tokentype == "identifier":
            category = "Class"
            role = "Used"
            itemcounter = identifier(indent, itemcounter, fileLineList, ofile, subrSymbolTable, category, role, token)
        #If it's not an identifier, do not indent. Add the token.
        else:
            itemcounter += 1

        #Check if current token is a varName. Obligatory if the previous was a "type".
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype == "identifier":

            kind = "argument"
            AddToSymbolTable(token, mtype, kind, subrSymbolTable) #Add the token, type, and kind to the symbol table.
            category = "argument" #varNames in parameterList are always arguments.
            role = "Defined"
            itemcounter = identifier(indent, itemcounter, fileLineList, ofile, subrSymbolTable, category, role, token)

            #Check if current token is a comma. If it is, keep going until parameters run out. Optional.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            while tokentype == "symbol" and token == ",":
                itemcounter += 1

                #Check if current token is a "type". Obligatory if the previous was a ,.
                tokentype = getTokenType(fileLineList[itemcounter])
                token = getToken(fileLineList[itemcounter])
                mtype = token
                typeflag = jacktype(tokentype, token)
                if typeflag == 1:
                    #If it's an identifier, put it under a new tag.
                    if tokentype == "identifier":
                        category = "Class"
                        role = "Used"
                        itemcounter = identifier(indent, itemcounter, fileLineList, ofile, subrSymbolTable, category, role, token)
                    #If it's not an identifier, do not indent. Add the token.
                    else:
                        itemcounter += 1
                    #Check if current token is a varName. Obligatory if 2x previous was a ,.
                    tokentype = getTokenType(fileLineList[itemcounter])
                    token = getToken(fileLineList[itemcounter])
                    if tokentype == "identifier":

                        kind = "argument"
                        AddToSymbolTable(token, mtype, kind, subrSymbolTable) #Add the token, type, and kind to the symbol table.
                        category = "argument" #varNames in parameterList are always arguments.
                        role = "Defined"
                        itemcounter = identifier(indent, itemcounter, fileLineList, ofile, subrSymbolTable, category, role, token)

                        #Update tokentype and token so that they are up to date for the while clause.
                        tokentype = getTokenType(fileLineList[itemcounter])
                        token = getToken(fileLineList[itemcounter])
                    else:
                        print("Error: parameterList does not have a valid varName after its comma!")
                else:
                    print("Error: parameterList does not have a valid type after its comma!")

        else:
            print("Error: parameterList first variable name not specified!")

    return itemcounter

def subroutineBody(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, constructorFlag, methodFlag, className):

    #Check if next character is a {. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        itemcounter += 1
    else:
        print("Error: subroutine body start { is not present!")

    #Check if next character is a variable declaration. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "keyword" and token == "var":
        itemcounter = varDec(indent, itemcounter, fileLineList, ofile, subrSymbolTable)
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])

    #Write number of arguments in function. Function definition.
    localVarCount = 0
    for item in subrSymbolTable:
        kind = GetKind(subrSymbolTable, item)
        if kind == "local":
            localVarCount += 1
    ofile.write(str(localVarCount) + "\n")

    if constructorFlag == True:
        fieldcount = 0
        for symbol in classSymbolTable:
            if GetKind(classSymbolTable, symbol) == "field":
                fieldcount += 1
        if fieldcount == 0:
            print("Note: no fields found in constructor's class.")

        #Push the field count to the stack, then find a free space in memory in order to store the field data for the object. Pop the result of Memory.alloc to pointer 0, so that "this" points to the base address of the object in question.
        ofile.write("push constant " + str(fieldcount) + "\n")
        ofile.write("call Memory.alloc 1\n")
        ofile.write("pop pointer 0\n")

    elif methodFlag == True:
        ofile.write("push argument 0\n")
        ofile.write("pop pointer 0\n")

    #Check what statement(s) (if any) are available.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    itemcounter = statements(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, methodFlag, className)

    #Check if next character is a }. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "}":
        itemcounter += 1
    else:
        print("Error: subroutine body end } is not present!")

    return itemcounter

def varDec(indent, itemcounter, fileLineList, ofile, subrSymbolTable):

    #Write var token.
    itemcounter += 1

    #Check if next token is a "type". Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    mtype = token
    typeflag = jacktype(tokentype, token)
    if typeflag == 1:
        #If it's an identifier, put it under a new tag.
        if tokentype == "identifier":
            category = "Class"
            role = "Used"
            itemcounter = identifier(indent, itemcounter, fileLineList, ofile, subrSymbolTable, category, role, token)
        #If it's not an identifier, do not indent. Add the token.
        else:
            itemcounter += 1
    else:
        print("Error: variable type not specified!")

    #Check if next token is an identifier (varName). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":

        kind = "local"
        AddToSymbolTable(token, mtype, kind, subrSymbolTable) #Add the token, type, and kind to the symbol table.
        category = "local" #varNames in parameterList are always arguments.
        role = "Defined"
        itemcounter = identifier(indent, itemcounter, fileLineList, ofile, subrSymbolTable, category, role, token)

    else:
        print("Error: variable name not specified!")

    #Check if next token is a ,. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    #If it was, loop through until variables run out (when commas run out). If no variable shows up after a comma, throw an error.
    while tokentype == "symbol" and token == ",":
        itemcounter += 1

        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype == "identifier":

            kind = "local"
            AddToSymbolTable(token, mtype, kind, subrSymbolTable) #Add the token, type, and kind to the symbol table.
            category = "local" #varNames in parameterList are always arguments.
            role = "Defined"
            itemcounter = identifier(indent, itemcounter, fileLineList, ofile, subrSymbolTable, category, role, token)

            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])

        else:
            print("Error: variable name not specified!")


    #Check if next token is a ;. Obligatory
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        itemcounter += 1
    else:
        print("Error: variable declaration does not end with a ;.")

    return itemcounter

def statements(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, methodFlag, className):

    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "keyword" and token in ("let", "if", "while", "do", "return"):
        if token == "let":
            itemcounter = letStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, methodFlag, className)
        elif token == "if":
            itemcounter = ifStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, methodFlag, voidFlag, className)
        elif token == "while":
            itemcounter = whileStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, methodFlag, voidFlag, className)
        elif token == "do":
            itemcounter = doStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, methodFlag, className)
        elif token == "return":
            itemcounter = returnStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, methodFlag, className)

        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])

    return itemcounter

def letStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, methodFlag, className):

    #Write let token.
    itemcounter += 1

    #Check if current token is an identifier (varName). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":

        #Find out which symbol table the token is in.
        if token in subrSymbolTable:
            mSymbolTable = subrSymbolTable #varName is either a local variable or an argument.
        elif token in classSymbolTable:
            mSymbolTable = classSymbolTable #varName is either a static variable or a field variable.
        else:
            print("Error: token is not in a symbol table!")
        category = GetKind(mSymbolTable, token)
        role = "Used"
        itemcounter = identifier(indent, itemcounter, fileLineList, ofile, mSymbolTable, category, role, token)

        #Remember which memory segment to pop to.
        mSegment = GetKind(mSymbolTable, token)
        if mSegment == "field": #If the segment is "field", we want to pop to "this" (pop to the object's fields).
            mSegment = "this"

        mIndex = GetIndex(mSymbolTable, token)
        #If the statement exists in a method and the token is in the argument segment, add 1 to the index since arg(0) is THIS.

    else:
        print("Error: variable name not specified!")

    #Check if varName is followed by an [, in which case it's an array. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "[":
        itemcounter += 1
        ArrayFlag = True

        #Push the array's base address onto the stack.
        ofile.write("push " + mSegment + " " + str(mIndex) + "\n")

        #If it's an array, check that it's a valid expression. Obligatory if varName was followed by an [.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        #Check if it's a valid expression by seeing if the first item (the term) is valid. The term is either an integerConstant, stringConstant, identifier, keyword with the contents "true" "false" "null" or "this", or a symbol with the contents "(" "-" or "~".
        #You can figure this out by following the each of the first tokens under the "term" field in the chart in the OneNote.
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            #Push the evaluated expression onto the stack.
            itemcounter = expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)
        else:
            print("Error: Invalid token type + token combination in array contents!")

        #Add the array's base address together with the evaluated expression. E.g in "let a[i]", we're going to add a + i. This gives us the base address of the "i"th entry of the array a.
        ofile.write("add\n")

        #Check if the next character is a ]. If it is, add it. Obligatory if varName was followed by an [.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype == "symbol" and token == "]":
            itemcounter += 1
        else:
            print("Error: array is not closed using square brackets!")
    else:
        ArrayFlag = False

    #Check if current token is "=". Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "=":
        itemcounter += 1
    else:
        print("Error: let statement lacks an =.")

    #ofile.write("Test2")

    #Check if current token is an expression. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)
    else:
        print("Error: Let statement is assigned to an invalid expression.")

    #Check if current token is ;. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        itemcounter += 1
    else:
        print("Error: Let statement does not finish with a ;")

    if ArrayFlag == False:
        #If the let statement is not an array, pop expression result to correct memory segment.
        ofile.write("pop " + mSegment + " " + str(mIndex) + "\n")
    else:
        #If the let statement is an array, the stack will have the value contained in the right array (or expression) on the top of the stack, with the base address of the left array under.
        #Pop the value into temp 0, and pop the left array base into pointer 1. Then fetch the value stored in temp 0 and pop it into the array at the correct index.
        ofile.write("pop temp 0\n")
        ofile.write("pop pointer 1\n")
        ofile.write("push temp 0\n")
        ofile.write("pop that 0\n")


    return itemcounter

def ifStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, methodFlag, className):

    #Write if token.
    itemcounter += 1

    #Check if current token is a parenthesis (. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "(":
        itemcounter += 1
    else:
        print("Error: if statement is not followed by an opening bracket!")

    #Check if current token is an expression. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)
    else:
        print("Error: If statement expression (the condition) is invalid .")

    ifLabel = "if" + str(itemcounter) #Label. Placed at the end of the if statement. Go there if the if-expression is false.
    #negate the expression in the if parentheses ().
    ofile.write("not\n")
    ofile.write("if-goto " + ifLabel + "\n")

    #Check if current token is a parenthesis ). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ")":
        itemcounter += 1
    else:
        print("Error: if statement is not followed by a closing bracket!")

    #Check if current token is a curly bracket {. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        itemcounter += 1
    else:
        print("Error: if statement condition is not followed by an opening curly bracket!")

    #Check what statement(s) (if any) are available.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    itemcounter = statements(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, methodFlag, className)

    #Check if current token is a curly bracket }. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "}":
        itemcounter += 1
    else:
        print("Error: if statement condition is not followed by a closing curly bracket!")

    elseLabel = "else" + str(itemcounter) #Label. Placed at the end of the else statement. Go there if the if-expression is true, once it has been run of course. Will also go there naturally after running the else statement. The actual itemcounter is irrelevant here, it's just used for a unique label.

    ofile.write("goto " + elseLabel + "\n") #Go to the elseLabel (end of the else statement) if the if-expression was true, since the if-statements will have run.
    ofile.write("label " + ifLabel + "\n") #This is where the if label will be. If the if statement was false, it will come here and run the else statement.

    #Check if current token is an "else" keyword. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "keyword" and token == "else":
        itemcounter += 1

        #Check if current token is a curly bracket {. Obligatory.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype == "symbol" and token == "{":
            itemcounter += 1

            #Check what statement(s) (if any) are available.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            itemcounter = statements(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, methodFlag, className)

            #Check if current token is a curly bracket }. Obligatory.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            if tokentype == "symbol" and token == "}":
                itemcounter += 1
            else:
                print("Error: else statement is not followed by a closing curly bracket!")
        else:
            print("Error: else statement is not followed by an opening curly bracket!")

    ofile.write("label " + elseLabel + "\n") #If the if statement was true, skip the else statement, jump here, and carry on.

    return itemcounter

def whileStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, methodFlag, className):

    #Write label for while loop to return to if the condition is still true.
    whileLoopStartLabel = "Wstart" + str(itemcounter)
    whileLoopEndLabel = "Wend" + str(itemcounter)
    ofile.write("label " + whileLoopStartLabel + "\n")

    #Write while token.
    itemcounter += 1

    #Check if current token is a parenthesis (. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "(":
        itemcounter += 1
    else:
        print("Error: if statement is not followed by an opening bracket!")

    #Check if current token is an expression. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)
    else:
        print("Error: If statement expression (the condition) is invalid .")

    #Check if current token is a parenthesis ). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ")":
        itemcounter += 1
    else:
        print("Error: if statement is not followed by a closing bracket!")

    #"not" the current expression. The expression is not-ed since you only when to exit the loop when it is no longer true (i.e exit the loop when the expression is false).
    ofile.write("not\n")
    ofile.write("if-goto " + whileLoopEndLabel + "\n")

    #Check if current token is a curly bracket {. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        itemcounter += 1
    else:
        print("Error: if statement condition is not followed by an opening curly bracket!")

    #Check what statement(s) (if any) are available.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    itemcounter = statements(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, methodFlag, className)

    #Check if current token is a curly bracket }. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "}":
        itemcounter += 1
    else:
        print("Error: if statement condition is not followed by a closing curly bracket!")

    ofile.write("goto " + whileLoopStartLabel + "\n")
    ofile.write("label " + whileLoopEndLabel + "\n")


    return itemcounter

def doStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, methodFlag, className):

    #Write do token.
    itemcounter += 1

    #Check if current token and next token are valid for a subroutineCall. subroutineCall starts with subroutineName/className/varName, which in turn is an identifier, and is then followed by either a "." or a "(".
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    nexttokentype = getTokenType(fileLineList[itemcounter + 1])
    nexttoken = getToken(fileLineList[itemcounter + 1])

    if token in subrSymbolTable or token in classSymbolTable:
        varName = True
    else:
        varName = False

    #subroutineCall starts with className.
    if tokentype == "identifier" and nexttokentype == "symbol" and nexttoken == "." and varName == False:
        tokentype = "className"
        itemcounter = subroutineCall(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, tokentype, className, methodFlag)

    #subroutineCall starts with varName.
    elif tokentype == "identifier" and nexttokentype == "symbol" and nexttoken == "." and varName == True:
        tokentype = "varName"
        itemcounter = subroutineCall(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, tokentype, className, methodFlag)

    #subroutineCall starts with subroutineName.
    elif tokentype == "identifier" and nexttokentype == "symbol" and nexttoken == "(":
        tokentype = "subroutineName"
        itemcounter = subroutineCall(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, tokentype, className, methodFlag)

    else:
        print("Error: Do statement does not contain a valid subroutineCall!")

    #Check if current token is a semicolon ;. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        itemcounter += 1
    else:
        print("Error: Do statement is not followed by a semicolon ;!")

    ofile.write("pop temp 0\n")

    return itemcounter

def returnStatement(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, voidFlag, methodFlag, className):

    #Write return token.
    itemcounter += 1

    #Check if current token is an expression. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)

    #Check if current token is a semicolon ;. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        itemcounter += 1
    else:
        print("Error: return statement is not followed by a semicolon ;!")

    #If subroutine return type is void, return 0.
    if voidFlag == True:
        ofile.write("push constant 0\n")

    #If subroutine is a constructor, return "this".
#    elif constructorFlag == True:
#        ofile.write("push pointer 0\n")

    ofile.write("return\n")

    return itemcounter

def expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag):

    #Add the term statement. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = term(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)
    else:
        print("Error: token is not a valid term statement!")

    #Check all remaining ops. Optional, as there may not be any.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "symbol" and token in ("+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="): #Note that &amp = &, &lt = <, and &gt = >. This is because the tokeniser makes them into these replacement characters.
        if token == "+":
            operator = "add\n"
        elif token == "-":
            operator = "sub\n"
        elif token == "*":
            operator = "call Math.multiply 2\n"
        elif token == "/":
            operator = "call Math.divide 2\n"
        elif token == "&amp;":
            operator = "and\n"
        elif token == "|":
            operator = "or\n"
        elif token == "&lt;":
            operator = "lt\n"
        elif token == "&gt;":
            operator = "gt\n"
        elif token == "=":
            operator = "eq\n"
        else:
            print("Error: symbol in expression not found!")

        itemcounter += 1

        #If there was an op, make sure the new current token is a term.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            itemcounter = term(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
        else:
            print("Error: token is not a valid term statement!")


        #Write the operator to operate on the terms.
        ofile.write(operator)

    return itemcounter

def term(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag):

    #term is either integerConstant or stringConstant
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    nexttokentype = getTokenType(fileLineList[itemcounter + 1])
    nexttoken = getToken(fileLineList[itemcounter + 1])

    #term is an integerConstant.
    if tokentype in ("integerConstant"):
        ofile.write("push constant " + token + "\n")
        itemcounter += 1

    #term is a stringConstant
    elif tokentype in ("stringConstant"):
        #First get the length of the string. Tell the OS to create a string of that length (1 argument, which is the length).
        ofile.write("push constant " + str(len(token)) + "\n")
        ofile.write("call String.new 1\n")
        #For each character, get its ASCII value, push that number as a constant, and then call String.appendchar to append it. String.appendchar takes 2 arguments: the current string object and the next character.
        for character in token:
            ofile.write("push constant " + str(ord(character)) + "\n")
            ofile.write("call String.appendChar 2\n")
        itemcounter += 1

    #term is a keywordConstant
    elif tokentype == "keyword" and token in ("true", "false", "null", "this"):
        if token in ("null", "false"):
            ofile.write("push constant 0\n")
        elif token == "true":
            ofile.write("push constant 1\nneg\n")
        elif token == "this":
            ofile.write("push pointer 0\n")
        itemcounter += 1

    #term is varName, and is neither followed by an "[" nor an "(".             (in the former case it would be an array, and in the latter case it would be a subroutineCall).
    elif tokentype == "identifier" and not (nexttokentype == "symbol" and nexttoken in ("[", "(", ".")):
        if token in classSymbolTable:
            mSymbolTable = classSymbolTable
        elif token in subrSymbolTable:
            mSymbolTable = subrSymbolTable
        else:
            print("Error: varName in term is not found in any symbol table!")

        mSegment = GetKind(mSymbolTable, token)
        if mSegment == "field":
            mSegment = "this" #If the segment is a field, change it to "this".
        mIndex = GetIndex(mSymbolTable, token)
        #If the segment is an argument and the subroutine is a method, add 1 to the index since arg[0] is THIS.
        if mSegment == "argument" and methodFlag == True:
            mIndex += 1
        ofile.write("push " + mSegment + " " + str(mIndex) + "\n")


        category = GetKind(mSymbolTable, token)
        role = "Used"
        itemcounter = identifier(indent, itemcounter, fileLineList, ofile, mSymbolTable, category, role, token)

    #term is varName, and is followed by an "[". Term is an array.
    elif tokentype == "identifier" and nexttokentype == "symbol" and nexttoken == "[":
        #Check what symbol table varName is in. Write the varName.
        if token in classSymbolTable:
            mSymbolTable = classSymbolTable
        elif token in subrSymbolTable:
            mSymbolTable = subrSymbolTable
        else:
            print("Error: varName (followed by [) in term is not found in any symbol table!")
        category = GetKind(mSymbolTable, token)
        role = "Used"
        itemcounter = identifier(indent, itemcounter, fileLineList, ofile, mSymbolTable, category, role, token)

        #Get the kind (field, argument, local, or static) of the array, as well as its index. I.e find out which variable it is.
        mKind = GetKind(mSymbolTable, token)
        if mKind == "field":
            mKind = "this"
        mIndex = GetIndex(mSymbolTable, token)

        #Push the array's base address to the stack.
        ofile.write("push " + mKind + " " + str(mIndex) + "\n")

        #Write the [.
        itemcounter += 1

        #Check if current token is a valid expression. Obligatory.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            itemcounter = expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)

            #Check if the next character is a ], then write it. Obligatory.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            if tokentype == "symbol" and token == "]":
                itemcounter += 1
            else:
                print("Error: varName[expression] is missing its closing bracket ]")
        else:
            print("Error: varName[expression] has an invalid expression.")

        ofile.write("add\n")
        ofile.write("pop pointer 1\n")
        ofile.write("push that 0\n")

    #term is subroutineCall. subroutineCall starts with subroutineName/className/varName, which in turn is an identifier, and is then followed by either a "." or a "(".
    elif tokentype == "identifier" and nexttokentype == "symbol" and nexttoken in ("(", "."):
#        itemcounter = subroutineCall(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable)

        if token in classSymbolTable or token in subrSymbolTable:
            varName = True
        else:
            varName = False

        #subroutineCall starts with className.
        if tokentype == "identifier" and nexttokentype == "symbol" and nexttoken == "." and varName == False:
            tokentype = "className"
            itemcounter = subroutineCall(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, tokentype, className, methodFlag)

        #subroutineCall starts with varName.
        elif tokentype == "identifier" and nexttokentype == "symbol" and nexttoken == "." and varName == True:
            tokentype = "varName"
            itemcounter = subroutineCall(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, tokentype, className, methodFlag)

        #subroutineCall starts with subroutineName.
        elif tokentype == "identifier" and nexttokentype == "symbol" and nexttoken == "(":
            tokentype = "subroutineName"
            itemcounter = subroutineCall(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, tokentype, className, methodFlag)

        else:
            print("Error: Do statement does not contain a valid subroutineCall!")




    #term is "(" expression ")".
    elif tokentype == "symbol" and token == "(":
        itemcounter += 1

        #Check if current token is a valid expression. Obligatory.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            itemcounter = expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)

            #Check if the next character is a ), then write it. Obligatory.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            if tokentype == "symbol" and token == ")":
                itemcounter += 1
            else:
                print('Error: "(" expression ")" is missing its closing parenthesis )')
        else:
            print('Error: "(" expression ")" has an invalid expresison.')

    #term is a unaryOp + term.
    elif tokentype == "symbol" and token in ("-", "~"):
        if token == "-":
            operator = "neg\n"
        elif token == "~":
            operator = "not\n"
        itemcounter += 1

        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        #Check if current token is a valid term. Obligatory.
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            itemcounter = term(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)
        else:
            print("Error: token is not a valid term statement!")

        #Apply operator. If it was -, negate the term. If it was ~, "not" the term.
        ofile.write(operator)

    else:
        print("Error: term couldn't find a fitting category.")

    return itemcounter

def subroutineCall(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, tokentype, className, methodFlag):
    #Note that subroutineCall isn't its own method in the API, so it does not have indentation for itself.
    #Also note that the subroutineCall can have ( className | varName ) '.' at the start. The rest of the syntax is the same whether it has it or not.

    callstring = "call "

    #Check if the subroutineCall is being done on a class, subroutine, or a variable.
    token = getToken(fileLineList[itemcounter])
    mSymbolTable = subrSymbolTable
    role = "Used"
    methodCallFlag = False
    if tokentype == "className":
        category = "Class"
    #subroutineCalls done on a subroutine are calling methods.
    elif tokentype == "subroutineName":
        category = "Subroutine"
        callstring += className + "."

        #Since we're going to call a method, we need to place the object at the top of the stack. Pointer 0 will already be set to the location of the object, so just push it.
        ofile.write("push pointer 0\n")
        methodCallFlag = True
    #Note that subroutineCalls done on a variable are also calling methods!
    elif tokentype == "varName":
        if token in classSymbolTable:
            mSymbolTable = classSymbolTable
        elif token in subrSymbolTable:
            mSymbolTable = subrSymbolTable
        else:
            print("Error: varName in subroutineCall is not found in any symbol table!")
        category = GetKind(mSymbolTable, token)

        objectSegment = GetKind(mSymbolTable, token) #Since we're calling a method, we need to find the object. If it is stored as local variable 2 for example, we need to push local 2 just before calling the function.
        if objectSegment == "field":
            objectSegment = "this"
        objectIndex = str(GetIndex(mSymbolTable, token)) #Find the object's index.

        token = GetType(mSymbolTable, token) #If the subroutineCall is being done on a variable, the function call must be on the variable's type. e.g in "var SquareGame game", "game" is the varName. "do game.run()" then becomes: "call SquareGame.run 1" in VM.
        methodCallFlag = True
        ofile.write("push " + objectSegment + " " + objectIndex + "\n") #Since we're calling an object, we want to push the object (the base address) and only afterwards do we push the regular arguments in the parentheses of the subroutine call.
    else:
        print("Error: subroutineCall starts with an invalid token type!")

    #Add to callstring. If the call is on a subroutine, adds the function name (the part that comes after "className."). If it is a method/class, adds the className (the part before the ".").
    callstring += token

    #Write subroutineName/className/varName, since validation should be done outside of this function beforehand.
    itemcounter = identifier(indent, itemcounter, fileLineList, ofile, mSymbolTable, category, role, token)

    #Check if the subroutine fits the following format: ( className | varName ) '.'
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    #If it does, write the .
    if tokentype == "symbol" and token == ".":
        #Add . to callstring.
        callstring += token
        itemcounter += 1

        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        #Next make sure the following token is the subroutineName. Obligatory.
        if tokentype == "identifier":
            #Add subroutineName to callstring.
            callstring += token
            category = "Subroutine"
            role = "Used"
            itemcounter = identifier(indent, itemcounter, fileLineList, ofile, mSymbolTable, category, role, token)

            #Fetch the newest token in order to carry on afterwards.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
        else:
            print("Error: subroutineCall className | varName is not followed by a .")

    #Carry on as before, as both versions of subroutineCall now continue in the same way.
    callstring += " " #Add space regardless of whether the subroutineCall is on a subroutineName, or a className/varName.subroutineName. This space is before the final number specifying the nArgs (arguments).

    #Check for opening parenthesis. Obligatory.
    if tokentype == "symbol" and token == "(":
        itemcounter += 1
    else:
        print("Error: subroutineCall does not have a ( after the subroutineName.")

    #Create an expressionList tag. Obligatory.
    itemcounter = expressionList(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, callstring, methodCallFlag, methodFlag, className)

    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    #Check for closing parenthesis. Obligatory.
    if tokentype == "symbol" and token == ")":
        itemcounter += 1
    else:
        print("Error: subroutineCall does not have a ) after the expressionList.")

    #print(subrSymbolTable)

    return itemcounter

def expressionList(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, callstring, methodCallFlag, methodFlag, className):

    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])

    expressioncount = 0

    #If we're calling a method, add 1 to the argument count.
    if methodCallFlag == True:
        expressioncount += 1

    #Check if there's a first expression. Optional.
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)
        expressioncount += 1

        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])

        #Check if there's another expression. If there is, keep going until there are none left. This is the case if the current token is a , (comma). Optional.
        while tokentype == "symbol" and token == ",":
            itemcounter += 1

            expressioncount += 1

            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            #Find the next expression. Obligatory if the , was present.
            if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
                itemcounter = expression(indent, itemcounter, fileLineList, ofile, classSymbolTable, subrSymbolTable, className, methodFlag)
                #Get the new current token.
                tokentype = getTokenType(fileLineList[itemcounter])
                token = getToken(fileLineList[itemcounter])
            else:
                print("Error: token is not a valid term statement! (expressionList)")

    ofile.write(callstring + str(expressioncount) + "\n")

    return itemcounter

#Verifies that the token is a valid "type".
def jacktype(tokentype, token):
    #This function checks if the token is of the type "type".
    if (tokentype == "keyword" and token in ("int", "char", "boolean")) or tokentype == "identifier":
        return 1
    else:
        return 0

#########################################################################################################################################################################

#Compiler functions.
def identifier(indent, itemcounter, fileLineList, ofile, symboltable, category, role, token):

    #Identifier is a class name or subroutine name.
    if category in ("Class", "Subroutine"):
#        ofile.write(indent + "<category> " + category + " </category>\n")
#        ofile.write(indent + "<role> " + role + " </role>\n")
#        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

    #Identifier is a variable.
    elif category in ("field", "static", "argument", "local"):
#        kind = GetKind(symboltable, token)
#        type = GetType(symboltable, token)
#        index = GetIndex(symboltable, token)

#        ofile.write(indent + "<category> " + category + " </category>\n")
#        ofile.write(indent + "<role> " + role + " </role>\n")
#        ofile.write(indent + "<index> " + str(index) + " </index>\n")
#        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

    return itemcounter

def AddToSymbolTable(symbolname, type, kind, symboltable):

    #List all of the values in the symbol table.
    mlist = list(symboltable.values())

    #Get the current count of the specified kind. E.g if there's already 2 static variables, set the index to be 2 (i.e 0, 1, 2).
    count = 0
    for item in mlist:
        if item[0] == kind:
            count += 1

    symboltable[symbolname] = [kind, type, count]

def GetKind(symboltable, token):
    return symboltable.get(token)[0]
def GetType(symboltable, token):
    return symboltable.get(token)[1]
def GetIndex(symboltable, token):
    return symboltable.get(token)[2]

#########################################################################################################################################################################

#Main starts here.
symbol = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"] #Define symbols
keyword = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"] #Define keywords

#Find all vm files in directory and open them.
filelist = list()
for mfile in os.listdir():
    if mfile.endswith(".jack") == True:
        filelist.append(mfile)
print("Directory .jack files to process:", filelist)


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
print("Tokenised files to process:", filelist)


#store the whole token file in a list.
for file in filelist:

    fileLineList = list()
    #Create name for output file.
#    outfilename = file.replace("T.xml", ".xml")
    outfilename = file.replace("T.xml", ".vm")
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
    #Look through the list of tokens and categorise them.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "keyword" and token == "class":
        classmethod(indent, itemcounter, fileLineList, ofile)

        itemcounter += 1

    ofile.close()


