# Import lexer function and token type constants from the lexer module
from testHaziqLexerKira import (
    lexer,
    tKeyword, tIdentifier, tInteger, tArith, tRel,
    tAssign, tLParen, tRParen, tLBrace, tRBrace, tSemicolon
)

# ==============================================================================
# PARSER FOR STATEMENTS AND BLOCKS (Functional Programming Paradigm)
# ==============================================================================

def make_node(label, children=()):
    """Constructs an immutable Abstract Syntax Tree (AST) node as a tuple."""
    return (label, tuple(children))


def expect(tokens, pos, expected_type, expected_value=None):
    """
    Pure helper function that validates the token at index `pos`.
    Returns a tuple of (matched_token, next_position) or raises a SyntaxError.
    """
    if pos >= len(tokens):
        target = f"'{expected_value}'" if expected_value else expected_type
        raise SyntaxError(f"SyntaxError at end of input: expected {target}")

    tok = tokens[pos]
    if tok.type != expected_type or (expected_value is not None and tok.value != expected_value):
        target = f"'{expected_value}'" if expected_value else expected_type
        raise SyntaxError(
            f"SyntaxError at line {tok.line}, col {tok.column}: "
            f"expected {target} before '{tok.value}'"
        )

    return tok, pos + 1


def parse_program(tokens, parse_expr, parse_cond):
    """
    Parses the top-level token stream into a 'Program' AST node.
    Grammar Rule: <program> -> <item> <item_list_tail>
    """
    if len(tokens) == 0:
        raise SyntaxError("SyntaxError at end of input: empty program")

    first_item, pos1 = parse_item(tokens, 0, parse_expr, parse_cond)
    rest_items, _ = parse_item_list_tail(tokens, pos1, parse_expr, parse_cond)
    return make_node("Program", (first_item,) + rest_items)


def parse_item_list_tail(tokens, pos, parse_expr, parse_cond):
    """
    Recursively parses remaining top-level items until the end of the token stream.
    Grammar Rule: <item_list_tail> -> <item> <item_list_tail> | ε
    """
    if pos >= len(tokens):
        return (), pos
    item, pos1 = parse_item(tokens, pos, parse_expr, parse_cond)
    rest, pos2 = parse_item_list_tail(tokens, pos1, parse_expr, parse_cond)
    return (item,) + rest, pos2


def parse_item(tokens, pos, parse_expr, parse_cond):
    """
    Dispatches a top-level item to either a variable declaration or a statement.
    Grammar Rule: <item> -> <decl> | <stmt>
    """
    tok = tokens[pos]
    if tok.type == tKeyword and tok.value == "let":
        return parse_decl(tokens, pos, parse_expr)
    return parse_stmt(tokens, pos, parse_expr, parse_cond)


def parse_decl(tokens, pos, parse_expr):
    """
    Parses a top-level variable declaration.
    Grammar Rule: <decl> -> 'let' id '=' <expr> ';'
    """
    _, pos1 = expect(tokens, pos, tKeyword, "let")
    id_tok, pos2 = expect(tokens, pos1, tIdentifier)
    _, pos3 = expect(tokens, pos2, tAssign, "=")
    expr_node, pos4 = parse_expr