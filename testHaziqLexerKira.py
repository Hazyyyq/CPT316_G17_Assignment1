# Declaring the token classes of Lexical Analyzer

# CREDITS: Youtube- @codewarehouse5175 
# Token given by the lecturer in the assignment, 
# not sure if it is correct way to write it or not, but I will use it for now

tKeyword = "KEYWORD"
tIdentifier = "IDENTIFIER"
tInteger = "INTEGER"
tArith = "ARITH"
tRel = "REL"
tAssign = "ASSIGN"
tLParen = "LPAREN"
tRParen = "RPAREN"
tLBrace = "LBRACE"
tRBrace = "RBRACE"
tSemicolon = "SEMICOLON"

#REMINDER: The lexer skips spaces, tabs, and newlines. 
#It also skips comments start with #. The lexer will not return any tokens for these characters.

class Token:
    def __init__(self, type, value, line,column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column


def lexer(text):
    count = 0
    tokens = []
    errors = []
    line = 1
    column = 1

    keywords = ["let", "if", "else", "while", "print"]

    while count < len(text):
        current_char = text[count]

        if current_char in '\t\r ':
            count += 1
            column += 1

        elif current_char == "\n":
            count += 1
            line += 1
            column = 1

        elif current_char == "#":
            while count < len(text) and text[count] != "\n":
                count += 1
                column += 1

        elif current_char.isalpha() or current_char == "_":
            identifier = ""
            start_column = column
            while count < len(text) and (text[count].isalnum() or text[count] == "_"):
                identifier += text[count]
                count += 1
                column += 1

            if identifier in keywords:
                tokens.append(Token(tKeyword, identifier, line, start_column))
            else:
                tokens.append(Token(tIdentifier, identifier, line, start_column))

        elif current_char.isdigit():
            start_column = column
            num = ""
        
            while count < len(text) and text[count].isdigit():
                num += text[count]
                count += 1
                column += 1    

            #reject digits followed by letters or underscores        
            if count < len(text) and (text[count].isalpha() or text[count] == "_"):

                reject_word = num
                while count < len(text) and (text[count].isalnum() or text[count] == "_"):
                    reject_word += text[count]
                    count += 1
                    column += 1
        
                errors.append("LexicalError at line {}, column {}: invalid sequence '{}'".format(line, start_column, reject_word))
                        
            else:
                tokens.append(Token(tInteger, int(num), line, start_column))
               

        elif current_char in "+-*/%":
            tokens.append(Token(tArith, current_char, line, column))
            count += 1
            column += 1
        elif current_char in "=!<>":
            start_column = column
            two_char = text[count:count + 2]

            #relationship operators options
            if two_char in ["==", "!=", "<=", ">="]:
                tokens.append(
                    Token(tRel, two_char, line, start_column)
                )
                count += 2
                column += 2

            elif current_char == "=":
                tokens.append(
                    Token(tAssign, current_char, line, start_column)
                )
                count += 1
                column += 1

            elif current_char in "<>":
                tokens.append(
                    Token(tRel, current_char, line, start_column)
                )
                count += 1
                column += 1

            else:
                errors.append(
                    "LexicalError at line {}, column {}: "
                    "invalid character '!'"
                    .format(line, start_column)
                )
                count += 1
                column += 1
    
        elif current_char == "(":
            tokens.append(Token(tLParen, current_char, line, column))
            count += 1
            column += 1
        elif current_char == ")":
            tokens.append(Token(tRParen, current_char, line, column))
            count += 1
            column += 1

        elif current_char == "{":
            tokens.append(Token(tLBrace, current_char, line, column))
            count += 1
            column += 1
        elif current_char == "}":
            tokens.append(Token(tRBrace, current_char, line, column))
            count += 1
            column += 1

        elif current_char == ";":
            tokens.append(Token(tSemicolon, current_char, line, column))
            count += 1
            column += 1

        else:
            errors.append(
                "LexicalError at line {}, column {}: "
                "invalid character '{}'"
                .format(line, column, current_char)
            )
            count += 1
            column += 1
# Maybe can simplify using OR expression, cuz Dr bundle them into Arith token, but I will leave it for now
        

    return tokens, errors

def print_token_stream(tokens):
    print("== TOKEN STREAM ==")
    print("LINE  COLUMN  TYPE        LEXEME")

    for token in tokens:
        print("{:4}  {:6}  {:11} {}".format(
            token.line,
            token.column,
            token.type,
            token.value
        ))

def print_token_counts(tokens):
    counts = {}

    for token in tokens:
        counts[token.type] = counts.get(token.type, 0) + 1

    print("\n== TOKEN COUNTS ==")
    print("Total tokens:", len(tokens))

    order = [
        tKeyword, tIdentifier, tInteger, tArith, tRel,
        tAssign, tLParen, tRParen, tLBrace, tRBrace,
        tSemicolon
    ]

    for token_type in order:
        if token_type in counts:
            print("  {:11} {}".format(
                token_type, counts[token_type]
            ))

with open("public4_lexical_errors.kira", "r") as file:
    text = file.read()

# Scan the source code
tokens, errors = lexer(text)

# Display the results
print_token_stream(tokens)
print_token_counts(tokens)

# Display lexical errors
if errors:
    print("\n== LEXICAL ERRORS ==")
    for error in errors:
        print(error)

#Will need to check again