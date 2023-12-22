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
    outfilename = file.replace("jack", "xml")
    ofile = open(outfilename, 'w') #output file

#Tokeniser
    #Return a list of tokens for the current file.
    wlist = tokeniser(file, symbol, keyword, numbers)

    #Take word list in the current file and use it to generate some xml.
    writeTokensToXML(wlist, ofile, symbol, keyword, numbers)




print(wlist)
