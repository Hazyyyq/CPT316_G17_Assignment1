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
    def __init__(self, type, value= None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value:
            return "{} : {}".format(self.type, self.value)
        else:
            return "{}".format(self.type)

def lexer(text):
    count = 0
    tokens = []

    while count < len(text):
        current_char = text[count]
        if current_char in '\t\n ':
            count += 1
        elif current_char == "+":
            tokens.append(Token(tArith, current_char))
            count += 1
        elif current_char == "-":
            tokens.append(Token(tArith, current_char))
            count += 1
        elif current_char == "*":
            tokens.append(Token(tArith, current_char))
            count += 1
        elif current_char == "/":
            tokens.append(Token(tArith, current_char))
            count += 1
        elif current_char == "%":
            tokens.append(Token(tArith, current_char))
            count += 1
# Maybe can simplify using OR expression, cuz Dr bundle them into Arith token, but I will leave it for now
        elif current_char.isdigit():
            this_char = current_char
            num = ""
            dotCount = 0
            while this_char.isdigit():
                num += current_char
                count += 1
                if count >= len(text):
                    break
                this_char = text[count]

                tokens.append(Token(tInteger, int(num)))

        else:
            print(format("LexicalError: invalid character '{0}'").format(current_char))
            count += 1

    return tokens

while True: 
    code = input("Enter code: ")
    result = lexer(code)
    print(result)

#Will need to check again