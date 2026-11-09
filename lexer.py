
tKeyword = "KEYWORD"
tIdentifier = "IDENTIFIER"
tInteger = "INTEGER"
tArith = "ARITH_OP"
tRel = "REL_OP"
tAssign = "ASSIGN"
tLParen = "LPAREN"
tRParen = "RPAREN"
tLBrace = "LBRACE"
tRBrace = "RBRACE"
tSemicolon = "SEMICOLON"

#The lexer skips spaces, tabs, newlines and comments start with #.
#The lexer will not return any tokens for these characters.

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
        
                errors.append("LexicalError at line {}, col {}: malformed token '{}'".format(line, start_column, reject_word))
                        
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
                    "LexicalError at line {}, col {}: " #can't use column as it shall be col instead
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

        elif current_char == '"':
            start_column = column
            bad_string = '"'
            count += 1
            column += 1

            # Consume everything until the closing quote or end of line/file
            while count < len(text) and text[count] not in '"\n':
                bad_string += text[count]
                count += 1
                column += 1

            if count < len(text) and text[count] == '"':
                bad_string += '"'
                count += 1
                column += 1
                errors.append(
                    f"LexicalError at line {line}, col {start_column}: "
                    f"strings are not supported '{bad_string}'"
                )
            else:
                errors.append(
                    f"LexicalError at line {line}, col {start_column}: "
                    f"unterminated string literal '{bad_string}'"
                )    

        else:
            errors.append(
                "LexicalError at line {}, col {}: "
                "invalid character '{}'"
                .format(line, column, current_char)
            )
            count += 1
            column += 1
        

    return tokens, errors

def print_token_stream(tokens):
    print("\n== TOKEN STREAM ==")
    print("LINE   COL  TYPE        LEXEME")

    for token in tokens:
        print("{:4}  {:4}  {:11} {}".format(
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
            print("  {:12} {}".format(
                token_type, counts[token_type]
            ))


if __name__ == "__main__":
    import sys

    filename = sys.argv[1] if len(sys.argv) > 1 else "public1_arithmetic_if.kira"

    try:
        with open(filename, "r") as file:
            text = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{filename}'.")
        sys.exit(1)

    tokens, errors = lexer(text)
    print_token_stream(tokens)

    if errors:
        for error in errors:
            print(error)

    print_token_counts(tokens)


