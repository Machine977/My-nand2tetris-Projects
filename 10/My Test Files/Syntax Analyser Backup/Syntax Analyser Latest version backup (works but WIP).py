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

    #Check if next item is a {. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: Class name keyword is not followed by a { token.")

    #Check if next item is a classVarDec (optional). Once finished, repeat again if the current token is still a classVarDec.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "keyword" and (token == "static" or token == "field"):
        itemcounter = classVarDec(indent, itemcounter, fileLineList, ofile)
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])

    #Check if next item is a subroutineDec (optional). Once finished, repeat again if the current token is still a subroutineDec.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "keyword" and (token == "constructor" or token == "function" or token == "method"):
        itemcounter = subroutineDec(indent, itemcounter, fileLineList, ofile)
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])


    #Check if next item is a }. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "}":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: Class content is not followed by a } token.")

    #Write class end tag
    ofile.write("</class>\n")

    return itemcounter

def classVarDec(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<classVarDec>\n")
    indent += "  "

    #Write static/field token.
    ofile.write(indent + fileLineList[itemcounter] + "\n")
    itemcounter += 1

    #Check if current token is a "type": either int, char, boolean, or a className. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    typeflag = type(tokentype, token)
    if typeflag == 1:
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: Class variable (field) type not declared!")

    #Check if current token is an identifier (varName). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: variable name not specified!")

    #Check if current token is a ,. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "symbol" and token == ",":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

        #Check if current token is an identifier (varName). Obligatory if preceded by a ,.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype == "identifier":
            ofile.write(indent + fileLineList[itemcounter] + "\n")
            itemcounter += 1
        else:
            print("Error: Class variable (field) name not specified after comma!")

    #Check if current token is a ;. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: variable name not specified!")

    indent = indent[:len(indent)-2]
    ofile.write(indent + "</classVarDec>\n")

    return itemcounter

def subroutineDec(indent, itemcounter, fileLineList, ofile):

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
    if typeflag == 1 or (tokentype == "keyword" and token == "void"):
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
    itemcounter = parameterList(indent, itemcounter, fileLineList, ofile)

    #Check if next item is a ). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ")":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        ofile.write("Error: subroutine definition end ) is not present!")

    #Check if next item is a subroutineBody. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        itemcounter = subroutineBody(indent, itemcounter, fileLineList, ofile)
    else:
        ofile.write("Error: subroutineBody doesn't start with a {!")

    #Write subroutineDec end tag.
    indent = indent[:len(indent)-2]
    ofile.write(indent + "</subroutineDec>\n")

    return itemcounter

def parameterList(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<parameterList>\n")
    indent += "  "

    #Check if current token is a "type": either int, char, boolean, or a className. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    typeflag = type(tokentype, token)
    if typeflag == 1:
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

        #Check if current token is a varName. Obligatory if the previous was a "type".
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype == "identifier":
            ofile.write(indent + fileLineList[itemcounter] + "\n")
            itemcounter += 1

            #Check if current token is a comma. If it is, keep going until parameters run out. Optional.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            while tokentype == "symbol" and token == ",":
                ofile.write(indent + fileLineList[itemcounter] + "\n")
                itemcounter += 1

                #Check if current token is a "type". Obligatory if the previous was a ,.
                tokentype = getTokenType(fileLineList[itemcounter])
                token = getToken(fileLineList[itemcounter])
                typeflag = type(tokentype, token)
                if typeflag == 1:
                    ofile.write(indent + fileLineList[itemcounter] + "\n")
                    itemcounter += 1

                    #Check if current token is a varName. Obligatory if 2x previous was a ,.
                    tokentype = getTokenType(fileLineList[itemcounter])
                    token = getToken(fileLineList[itemcounter])
                    if tokentype == "identifier":
                        ofile.write(indent + fileLineList[itemcounter] + "\n")
                        itemcounter += 1
                    else:
                        print("Error: parameterList does not have a valid varName after its comma!")
                else:
                    print("Error: parameterList does not have a valid type after its comma!")

        else:
            print("Error: variable name not specified!")


    indent = indent[:len(indent)-2]
    ofile.write(indent + "</parameterList>\n")

    return itemcounter

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
    while tokentype == "keyword" and token == "var":
        itemcounter = varDec(indent, itemcounter, fileLineList, ofile)
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])

    #Check what statement(s) (if any) are available.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    itemcounter = statements(indent, itemcounter, fileLineList, ofile)

    #Check if next character is a }. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "}":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: subroutine body end } is not present!")

    #Write subroutineBody end tag.
    indent = indent[:len(indent)-2]
    ofile.write(indent + "</subroutineBody>\n")

    return itemcounter

def varDec(indent, itemcounter, fileLineList, ofile):
    ofile.write(indent + "<varDec>\n")
    indent += "  "

    #Write var token.
    ofile.write(indent + fileLineList[itemcounter] + "\n")
    itemcounter += 1

    #Check if next token is a "type". Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    typeflag = type(tokentype, token)
    if typeflag == 1:
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: variable type not specified!")

    #Check if next token is an identifier (varName). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: variable name not specified!")

    #Check if next token is a ,. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    #If it was, loop through until variables run out (when commas run out). If no variable shows up after a comma, throw an error.
    while tokentype == "symbol" and token == ",":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

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

    indent = indent[:len(indent)-2]
    ofile.write(indent + "</varDec>\n")

    return itemcounter

def statements(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<statements>\n")
    indent += "  "

    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "keyword" and token in ("let", "if", "while", "do", "return"):
        if token == "let":
            itemcounter = letStatement(indent, itemcounter, fileLineList, ofile)
        elif token == "if":
            itemcounter = ifStatement(indent, itemcounter, fileLineList, ofile)
        elif token == "while":
            itemcounter = whileStatement(indent, itemcounter, fileLineList, ofile)
        elif token == "do":
            itemcounter = doStatement(indent, itemcounter, fileLineList, ofile)
        elif token == "return":
            itemcounter = returnStatement(indent, itemcounter, fileLineList, ofile)

        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        print("tokentype = " + str(tokentype) + " token = " + token + " itemcounter = " + str(itemcounter))
#        if itemcounter == 48:
#            break

        #itemcounter += 1

    indent = indent[:len(indent)-2]
    ofile.write(indent + "</statements>\n")

    return itemcounter

def letStatement(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<letStatement>\n")
    indent += "  "

    print(itemcounter)

    #Write let token.
    ofile.write(indent + fileLineList[itemcounter] + "\n")
    itemcounter += 1

    #Check if current token is an identifier (varName). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "identifier":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: variable name not specified!")

    #Check if varName is followed by an [, in which case it's an array. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "[":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

        #If it's an array, check that it's a valid expression. Obligatory if varName was followed by an [.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        #Check if it's a valid expression by seeing if the first item (the term) is valid. The term is either an integerConstant, stringConstant, identifier, keyword with the contents "true" "false" "null" or "this", or a symbol with the contents "(" "-" or "~".
        #You can figure this out by following the each of the first tokens under the "term" field in the chart in the OneNote.
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            itemcounter = expression(indent, itemcounter, fileLineList, ofile)
        else:
            print("Error: Invalid token type + token combination in array contents!")

        #Check if the next character is a ]. If it is, add it. Obligatory if varName was followed by an [.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype == "symbol" and token == "]":
            ofile.write(indent + fileLineList[itemcounter] + "\n")
            itemcounter += 1
        else:
            print("Error: array is not closed using square brackets!")

    #Check if current token is "=". Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "=":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: let statement lacks an =.")

    #Check if current token is an expression. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile)
    else:
        print("Error: Let statement is assigned to an invalid expression.")

    #Check if current token is ;. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: Let statement does not finish with a ;")

    indent = indent[:len(indent)-2]
    ofile.write(indent + "</letStatement>\n")

    return itemcounter

def ifStatement(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<ifStatement>\n")
    indent += "  "

    #Write if token.
    ofile.write(indent + fileLineList[itemcounter] + "\n")
    itemcounter += 1

    #Check if current token is a parenthesis (. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "(":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: if statement is not followed by an opening bracket!")

    #Check if current token is an expression. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile)
    else:
        print("Error: If statement expression (the condition) is invalid .")

    #Check if current token is a parenthesis ). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ")":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: if statement is not followed by a closing bracket!")

    #Check if current token is a curly bracket {. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: if statement condition is not followed by an opening curly bracket!")

    #Check what statement(s) (if any) are available.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    itemcounter = statements(indent, itemcounter, fileLineList, ofile)

    #Check if current token is a curly bracket }. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "}":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: if statement condition is not followed by a closing curly bracket!")

    #Check if current token is an "else" keyword. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "keyword" and token == "else":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

        #Check if current token is a curly bracket {. Obligatory.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype == "symbol" and token == "{":
            ofile.write(indent + fileLineList[itemcounter] + "\n")
            itemcounter += 1

            #Check what statement(s) (if any) are available.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            itemcounter = statements(indent, itemcounter, fileLineList, ofile)

            #Check if current token is a curly bracket }. Obligatory.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            if tokentype == "symbol" and token == "}":
                ofile.write(indent + fileLineList[itemcounter] + "\n")
                itemcounter += 1
            else:
                print("Error: else statement is not followed by a closing curly bracket!")
        else:
            print("Error: else statement is not followed by an opening curly bracket!")


    indent = indent[:len(indent)-2]
    ofile.write(indent + "</ifStatement>\n")

    return itemcounter

def whileStatement(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<whileStatement>\n")
    indent += "  "

    #Write while token.
    ofile.write(indent + fileLineList[itemcounter] + "\n")
    itemcounter += 1

    #Check if current token is a parenthesis (. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "(":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: if statement is not followed by an opening bracket!")

    #Check if current token is an expression. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile)
    else:
        print("Error: If statement expression (the condition) is invalid .")

    #Check if current token is a parenthesis ). Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ")":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: if statement is not followed by a closing bracket!")

    #Check if current token is a curly bracket {. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "{":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: if statement condition is not followed by an opening curly bracket!")

    #Check what statement(s) (if any) are available.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    itemcounter = statements(indent, itemcounter, fileLineList, ofile)

    #Check if current token is a curly bracket }. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == "}":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: if statement condition is not followed by a closing curly bracket!")

    indent = indent[:len(indent)-2]
    ofile.write(indent + "</whileStatement>\n")

    return itemcounter

def doStatement(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<doStatement>\n")
    indent += "  "

    #Write do token.
    ofile.write(indent + fileLineList[itemcounter] + "\n")
    itemcounter += 1

    #Check if current token and next token are valid for a subroutineCall. subroutineCall starts with subroutineName/className/varName, which in turn is an identifier, and is then followed by either a "." or a "(".
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    nexttokentype = getTokenType(fileLineList[itemcounter + 1])
    nexttoken = getToken(fileLineList[itemcounter + 1])
    if tokentype == "identifier" and nexttokentype == "symbol" and nexttoken in ("(", "."):
        itemcounter = subroutineCall(indent, itemcounter, fileLineList, ofile)
    else:
        print("Error: Do statement does not contain a valid subroutineCall!")

    #Check if current token is a semicolon ;. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: Do statement is not followed by a semicolon ;!")

    indent = indent[:len(indent)-2]
    ofile.write(indent + "</doStatement>\n")

    return itemcounter

def returnStatement(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<returnStatement>\n")
    indent += "  "

    #Write return token.
    ofile.write(indent + fileLineList[itemcounter] + "\n")
    itemcounter += 1

    #Check if current token is an expression. Optional.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile)

    #Check if current token is a semicolon ;. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "symbol" and token == ";":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: return statement is not followed by a semicolon ;!")

    indent = indent[:len(indent)-2]
    ofile.write(indent + "</returnStatement>\n")

    return itemcounter

def expression(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<expression>\n")
    indent += "  "

    #Add the term statement. Obligatory.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = term(indent, itemcounter, fileLineList, ofile)
    else:
        print("Error: token is not a valid term statement!")

    #Check all remaining ops. Optional, as there may not be any.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    while tokentype == "symbol" and token in ("+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="): #Note that &amp = &, &lt = <, and &gt = >. This is because the tokeniser makes them into these replacement characters.
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

        #If there was an op, make sure the new current token is a term.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            itemcounter = term(indent, itemcounter, fileLineList, ofile)
        else:
            print("Error: token is not a valid term statement!")


    indent = indent[:len(indent)-2]
    ofile.write(indent + "</expression>\n")

    return itemcounter

def term(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<term>\n")
    indent += "  "

    #term is either integerConstant or stringConstant
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    nexttokentype = getTokenType(fileLineList[itemcounter + 1])
    nexttoken = getToken(fileLineList[itemcounter + 1])

    if tokentype in ("integerConstant", "stringConstant"):
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

    #term is a keywordConstant
    elif tokentype == "keyword" and token in ("true", "false", "null", "this"):
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

    #term is varName, and is neither followed by an "[" nor an "(".             (in the former case it would be an array, and in the latter case it would be a subroutineCall).
    elif tokentype == "identifier" and not (nexttokentype == "symbol" and nexttoken in ("[", "(", ".")):
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

    #term is varName, and is followed by an "[".
    elif tokentype == "identifier" and nexttokentype == "symbol" and nexttoken == "[":
        #Write the varName.
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
        #Write the [.
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

        #Check if current token is a valid expression. Obligatory.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            itemcounter = expression(indent, itemcounter, fileLineList, ofile)

            #Check if the next character is a ], then write it. Obligatory.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            if tokentype == "symbol" and token == "]":
                ofile.write(indent + fileLineList[itemcounter] + "\n")
                itemcounter += 1
            else:
                print("Error: varName[expression] is missing its closing bracket ]")
        else:
            print("Error: varName[expression] has an invalid expression.")

    #term is subroutineCall. subroutineCall starts with subroutineName/className/varName, which in turn is an identifier, and is then followed by either a "." or a "(".
    elif tokentype == "identifier" and nexttokentype == "symbol" and nexttoken in ("(", "."):
        itemcounter = subroutineCall(indent, itemcounter, fileLineList, ofile)

    #term is "(" expression ")".
    elif tokentype == "symbol" and token == "(":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

        #Check if current token is a valid expression. Obligatory.
        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            itemcounter = expression(indent, itemcounter, fileLineList, ofile)

            #Check if the next character is a ), then write it. Obligatory.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            if tokentype == "symbol" and token == ")":
                ofile.write(indent + fileLineList[itemcounter] + "\n")
                itemcounter += 1
            else:
                print('Error: "(" expression ")" is missing its closing parenthesis )')
        else:
            print('Error: "(" expression ")" has an invalid expresison.')

    #term is a unaryOp + term.
    elif tokentype == "symbol" and token in ("-", "~"):
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        #Check if current token is a valid term. Obligatory.
        if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
            itemcounter = term(indent, itemcounter, fileLineList, ofile)
        else:
            print("Error: token is not a valid term statement!")

    else:
        print("Error: term couldn't find a fitting category.")


    indent = indent[:len(indent)-2]
    ofile.write(indent + "</term>\n")

    return itemcounter

def subroutineCall(indent, itemcounter, fileLineList, ofile):
    #Note that subroutineCall isn't its own method in the API, so it does not have indentation for itself.
    #Also note that the subroutineCall can have ( className | varName ) '.' at the start. The rest of the syntax is the same whether it has it or not.


    #Write subroutineName/className/varName, since validation should be done outside of this function.
    ofile.write(indent + fileLineList[itemcounter] + "\n")
    itemcounter += 1

    #Check if the subroutine fits the following format: ( className | varName ) '.'
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    #If it does, write the .
    if tokentype == "symbol" and token == ".":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1

        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])
        #Next make sure the following token is the subroutineName. Obligatory.
        if tokentype == "identifier":
            ofile.write(indent + fileLineList[itemcounter] + "\n")
            itemcounter += 1
            #Fetch the newest token in order to carry on afterwards.
            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
        else:
            print("Error: subroutineCall className | varName is not followed by a .")

    #Carry on as before, as both versions of subroutineCall now continue in the same way.

    #Check for opening parenthesis. Obligatory.
    if tokentype == "symbol" and token == "(":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: subroutineCall does not have a ( after the subroutineName.")

    #Create an expressionList tag. Obligatory.
    itemcounter = expressionList(indent, itemcounter, fileLineList, ofile)

    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    #Check for closing parenthesis. Obligatory.
    if tokentype == "symbol" and token == ")":
        ofile.write(indent + fileLineList[itemcounter] + "\n")
        itemcounter += 1
    else:
        print("Error: subroutineCall does not have a ) after the expressionList.")

    return itemcounter

def expressionList(indent, itemcounter, fileLineList, ofile):

    ofile.write(indent + "<expressionList>\n")
    indent += "  "

    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])

    #Check if there's a first expression. Optional.
    if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
        itemcounter = expression(indent, itemcounter, fileLineList, ofile)

        tokentype = getTokenType(fileLineList[itemcounter])
        token = getToken(fileLineList[itemcounter])

        #Check if there's another expression. If there is, keep going until there are none left. This is the case if the current token is a , (comma). Optional.
        while tokentype == "symbol" and token == ",":
            ofile.write(indent + fileLineList[itemcounter] + "\n")
            itemcounter += 1

            tokentype = getTokenType(fileLineList[itemcounter])
            token = getToken(fileLineList[itemcounter])
            #Find the next expression. Obligatory if the , was present.
            if tokentype in ("integerConstant", "stringConstant", "identifier") or (tokentype == "keyword" and token in ("true", "false", "null", "this")) or (tokentype == "symbol" and token in ("(", "-", "~")):
                itemcounter = expression(indent, itemcounter, fileLineList, ofile)
                #Get the new current token.
                tokentype = getTokenType(fileLineList[itemcounter])
                token = getToken(fileLineList[itemcounter])
            else:
                print("Error: token is not a valid term statement! (expressionList)")


    indent = indent[:len(indent)-2]
    ofile.write(indent + "</expressionList>\n")

    return itemcounter

#Verifies that the token is a valid "type".
def type(tokentype, token):
    #This function checks if the token is of the type "type".
    if (tokentype == "keyword" and token in ("int", "char", "boolean")) or tokentype == "identifier":
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
    #Look through the list of tokens and categorise them.
    tokentype = getTokenType(fileLineList[itemcounter])
    token = getToken(fileLineList[itemcounter])
    if tokentype == "keyword" and token == "class":
        classmethod(indent, itemcounter, fileLineList, ofile)

        itemcounter += 1

    ofile.close()


#print(fileLineList)


#Create a function that contains all types of XML tags, and make it recursively run.


#print(wlist)
