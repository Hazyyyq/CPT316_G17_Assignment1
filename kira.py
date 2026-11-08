import sys
import os
from lexer import (
    lexer, print_token_stream, print_token_counts
)
from parser import (
    run_statement_parser, parse_expr, parse_cond, print_ast
)

def main():
    # 1. Read input filename from command line (defaults to public1 if none provided)
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "public1_arithmetic_if.kira"

    if not os.path.exists(filename):
        print(f"Error: Could not find '{filename}'.")
        sys.exit(1)

    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()

    # 2. Run Lexer
    tokens, errors = lexer(text)

    # Section 1: Token Stream
    print_token_stream(tokens)

    # Report ALL lexical errors immediately below the stream
    if errors:
        for err in errors:
            print(err)

    # Section 2: Token Counts
    print_token_counts(tokens)

    # If any lexical errors exist, do NOT run the parser
    if errors:
        print(f"\n{len(errors)} lexical error(s). Parsing skipped.")
        sys.exit(0)

    # Section 3: Abstract Syntax Tree or Syntax Error
    print("\n== AST ==")
    try:
        ast_root = run_statement_parser(parse_expr, parse_cond, tokens, errors)
        print_ast(ast_root)
    except SyntaxError as e:
        # Catches grammar violations cleanly without a Python stack trace
        print(e)
    except Exception as e:
        # Failsafe fallback to ensure no crash or unhandled traceback
        print(f"SyntaxError: {e}")

if __name__ == "__main__":
    main()