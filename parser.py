from testHaziqLexerKira import (
    lexer, tokens, errors,
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


def parse_decl(tokens, pos, parse_expr):
    """
    Parses a top-level variable declaration.
    Grammar Rule: <decl> -> 'let' id '=' <expr> ';'
    """
    _, pos1 = expect(tokens, pos, tKeyword, "let")
    id_tok, pos2 = expect(tokens, pos1, tIdentifier)
    _, pos3 = expect(tokens, pos2, tAssign, "=")
    expr_node, pos4 = parse_expr(tokens, pos3)      # Delegates expression parsing
    _, pos5 = expect(tokens, pos4, tSemicolon, ";")
    return make_node(f"Let {id_tok.value}", (expr_node,)), pos5


def parse_assign(tokens, pos, parse_expr):
    """
    Parses an assignment statement.
    Grammar Rule: <assign> -> id '=' <expr> ';'
    """
    id_tok, pos1 = expect(tokens, pos, tIdentifier)
    _, pos2 = expect(tokens, pos1, tAssign, "=")
    expr_node, pos3 = parse_expr(tokens, pos2)      # Delegates expression parsing
    _, pos4 = expect(tokens, pos3, tSemicolon, ";")
    return make_node(f"Assign {id_tok.value}", (expr_node,)), pos4


def parse_print_stmt(tokens, pos, parse_expr):
    """
    Parses a print statement.
    Grammar Rule: <print_stmt> -> 'print' '(' <expr> ')' ';'
    """
    _, pos1 = expect(tokens, pos, tKeyword, "print")
    _, pos2 = expect(tokens, pos1, tLParen, "(")
    expr_node, pos3 = parse_expr(tokens, pos2)      # Delegates expression parsing
    _, pos4 = expect(tokens, pos3, tRParen, ")")
    _, pos5 = expect(tokens, pos4, tSemicolon, ";")
    return make_node("Print", (expr_node,)), pos5


def parse_while_stmt(tokens, pos, parse_expr, parse_cond):
    """
    Parses a while-loop statement.
    Grammar Rule: <while_stmt> -> 'while' '(' <cond> ')' <block>
    """
    _, pos1 = expect(tokens, pos, tKeyword, "while")
    _, pos2 = expect(tokens, pos1, tLParen, "(")
    cond_node, pos3 = parse_cond(tokens, pos2)      # Delegates condition parsing
    _, pos4 = expect(tokens, pos3, tRParen, ")")
    body_node, pos5 = parse_block(tokens, pos4, "Body", parse_expr, parse_cond)
    return make_node("While", (cond_node, body_node)), pos5


def parse_if_stmt(tokens, pos, parse_expr, parse_cond):
    """
    Parses a conditional if-statement with an optional else-branch.
    Grammar Rule: <if_stmt> -> 'if' '(' <cond> ')' <block> ['else' <block>]
    """
    _, pos1 = expect(tokens, pos, tKeyword, "if")
    _, pos2 = expect(tokens, pos1, tLParen, "(")
    cond_node, pos3 = parse_cond(tokens, pos2)      # Delegates condition parsing
    _, pos4 = expect(tokens, pos3, tRParen, ")")
    then_node, pos5 = parse_block(tokens, pos4, "Then", parse_expr, parse_cond)

    # Check for an optional 'else' block
    if pos5 < len(tokens) and tokens[pos5].type == tKeyword and tokens[pos5].value == "else":
        _, pos6 = expect(tokens, pos5, tKeyword, "else")
        else_node, pos7 = parse_block(tokens, pos6, "Else", parse_expr, parse_cond)
        return make_node("If", (cond_node, then_node, else_node)), pos7

    return make_node("If", (cond_node, then_node)), pos5


def parse_stmt_list_tail(tokens, pos, parse_expr, parse_cond):
    """
    Recursively parses subsequent statements inside a block until '}' is reached.
    Grammar Rule: <stmt_list_tail> -> <stmt> <stmt_list_tail> | ε
    """
    if pos >= len(tokens):
        raise SyntaxError("SyntaxError at end of input: expected '}'")
    if tokens[pos].type == tRBrace:
        return (), pos
    stmt, pos1 = parse_stmt(tokens, pos, parse_expr, parse_cond)
    rest, pos2 = parse_stmt_list_tail(tokens, pos1, parse_expr, parse_cond)
    return (stmt,) + rest, pos2


def parse_block(tokens, pos, block_label, parse_expr, parse_cond):
    """
    Parses a brace-enclosed block containing one or more statements.
    Grammar Rule: <block> -> '{' <stmt> <stmt_list_tail> '}'
    """
    _, pos1 = expect(tokens, pos, tLBrace, "{")
    first_stmt, pos2 = parse_stmt(tokens, pos1, parse_expr, parse_cond)
    rest_stmts, pos3 = parse_stmt_list_tail(tokens, pos2, parse_expr, parse_cond)
    _, pos4 = expect(tokens, pos3, tRBrace, "}")
    return make_node(block_label, (first_stmt,) + rest_stmts), pos4


def parse_stmt(tokens, pos, parse_expr, parse_cond):
    """
    Dispatches a statement based on the current lookahead token.
    Grammar Rule: <stmt> -> <assign> | <if_stmt> | <while_stmt> | <print_stmt>
    """
    if pos >= len(tokens):
        raise SyntaxError("SyntaxError at end of input: expected statement")

    tok = tokens[pos]
    if tok.type == tIdentifier:
        return parse_assign(tokens, pos, parse_expr)
    if tok.type == tKeyword:
        if tok.value == "if":
            return parse_if_stmt(tokens, pos, parse_expr, parse_cond)
        if tok.value == "while":
            return parse_while_stmt(tokens, pos, parse_expr, parse_cond)
        if tok.value == "print":
            return parse_print_stmt(tokens, pos, parse_expr)
        if tok.value == "let":
            # Variable declarations ('let') are restricted to the top level
            raise SyntaxError(
                f"SyntaxError at line {tok.line}, col {tok.column}: "
                f"'let' declaration is not allowed inside a block"
            )

    raise SyntaxError(
        f"SyntaxError at line {tok.line}, col {tok.column}: "
        f"unexpected token '{tok.value}'"
    )


def parse_item(tokens, pos, parse_expr, parse_cond):
    """
    Dispatches a top-level item to either a variable declaration or a statement.
    Grammar Rule: <item> -> <decl> | <stmt>
    """
    tok = tokens[pos]
    if tok.type == tKeyword and tok.value == "let":
        return parse_decl(tokens, pos, parse_expr)
    return parse_stmt(tokens, pos, parse_expr, parse_cond)


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


def run_statement_parser(parse_expr_fn, parse_cond_fn, token_stream=tokens, error_list=errors):
    """Receives tokens and errors from the lexer and runs the parser if valid."""
    if error_list:
        return None
    return parse_program(tuple(token_stream), parse_expr_fn, parse_cond_fn)