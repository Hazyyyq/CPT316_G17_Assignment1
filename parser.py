from lexer import (
    lexer,
    tKeyword, tIdentifier, tInteger, tArith, tRel,
    tAssign, tLParen, tRParen, tLBrace, tRBrace, tSemicolon
)

# ==============================================================================
# PARSER FOR STATEMENTS AND BLOCKS (Functional Programming Paradigm)
# ==============================================================================

def make_node(label, children=()):
    """Constructs an immutable AST node as a tuple."""
    return (label, tuple(children))


def expect(tokens, pos, expected_type, expected_value=None):
    """
    Pure validation helper.
    Returns (matched_token, next_pos) or raises SyntaxError.
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


# --- Statements ---

def parse_decl(tokens, pos, parse_expr):
    """Grammar: <decl> -> 'let' id '=' <expr> ';'"""
    _, pos1 = expect(tokens, pos, tKeyword, "let")
    id_tok, pos2 = expect(tokens, pos1, tIdentifier)
    _, pos3 = expect(tokens, pos2, tAssign, "=")
    expr_node, pos4 = parse_expr(tokens, pos3)
    _, pos5 = expect(tokens, pos4, tSemicolon, ";")
    return make_node(f"Let {id_tok.value}", (expr_node,)), pos5


def parse_assign(tokens, pos, parse_expr):
    """Grammar: <assign> -> id '=' <expr> ';'"""
    id_tok, pos1 = expect(tokens, pos, tIdentifier)
    _, pos2 = expect(tokens, pos1, tAssign, "=")
    expr_node, pos3 = parse_expr(tokens, pos2)
    _, pos4 = expect(tokens, pos3, tSemicolon, ";")
    return make_node(f"Assign {id_tok.value}", (expr_node,)), pos4


def parse_print_stmt(tokens, pos, parse_expr):
    """Grammar: <print_stmt> -> 'print' '(' <expr> ')' ';'"""
    _, pos1 = expect(tokens, pos, tKeyword, "print")
    _, pos2 = expect(tokens, pos1, tLParen, "(")
    expr_node, pos3 = parse_expr(tokens, pos2)
    _, pos4 = expect(tokens, pos3, tRParen, ")")
    _, pos5 = expect(tokens, pos4, tSemicolon, ";")
    return make_node("Print", (expr_node,)), pos5


def parse_while_stmt(tokens, pos, parse_expr, parse_cond):
    """Grammar: <while_stmt> -> 'while' '(' <cond> ')' <block>"""
    _, pos1 = expect(tokens, pos, tKeyword, "while")
    _, pos2 = expect(tokens, pos1, tLParen, "(")
    cond_node, pos3 = parse_cond(tokens, pos2)
    _, pos4 = expect(tokens, pos3, tRParen, ")")
    body_node, pos5 = parse_block(tokens, pos4, "Body", parse_expr, parse_cond)
    return make_node("While", (cond_node, body_node)), pos5


def parse_if_stmt(tokens, pos, parse_expr, parse_cond):
    """Grammar: <if_stmt> -> 'if' '(' <cond> ')' <block> ['else' <block>]"""
    _, pos1 = expect(tokens, pos, tKeyword, "if")
    _, pos2 = expect(tokens, pos1, tLParen, "(")
    cond_node, pos3 = parse_cond(tokens, pos2)
    _, pos4 = expect(tokens, pos3, tRParen, ")")
    then_node, pos5 = parse_block(tokens, pos4, "Then", parse_expr, parse_cond)

    if pos5 < len(tokens) and tokens[pos5].type == tKeyword and tokens[pos5].value == "else":
        _, pos6 = expect(tokens, pos5, tKeyword, "else")
        else_node, pos7 = parse_block(tokens, pos6, "Else", parse_expr, parse_cond)
        return make_node("If", (cond_node, then_node, else_node)), pos7

    return make_node("If", (cond_node, then_node)), pos5


# --- Blocks ---

def parse_stmt_list_tail(tokens, pos, parse_expr, parse_cond):
    """Recursively parses subsequent statements in a block until '}'."""
    if pos >= len(tokens):
        raise SyntaxError("SyntaxError at end of input: expected '}'")
    if tokens[pos].type == tRBrace:
        return (), pos
    stmt, pos1 = parse_stmt(tokens, pos, parse_expr, parse_cond)
    rest, pos2 = parse_stmt_list_tail(tokens, pos1, parse_expr, parse_cond)
    return (stmt,) + rest, pos2


def parse_block(tokens, pos, block_label, parse_expr, parse_cond):
    """Grammar: <block> -> '{' <stmt> <stmt_list_tail> '}'"""
    _, pos1 = expect(tokens, pos, tLBrace, "{")
    first_stmt, pos2 = parse_stmt(tokens, pos1, parse_expr, parse_cond)
    rest_stmts, pos3 = parse_stmt_list_tail(tokens, pos2, parse_expr, parse_cond)
    _, pos4 = expect(tokens, pos3, tRBrace, "}")
    return make_node(block_label, (first_stmt,) + rest_stmts), pos4


def parse_stmt(tokens, pos, parse_expr, parse_cond):
    """Dispatches a single statement based on lookahead."""
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
            raise SyntaxError(
                f"SyntaxError at line {tok.line}, col {tok.column}: "
                f"'let' declaration is not allowed inside a block"
            )

    raise SyntaxError(
        f"SyntaxError at line {tok.line}, col {tok.column}: "
        f"unexpected token '{tok.value}'"
    )


# --- Program Entry ---

def parse_item(tokens, pos, parse_expr, parse_cond):
    """<item> -> <decl> | <stmt>"""
    if pos >= len(tokens):
        raise SyntaxError("SyntaxError at end of input: expected declaration or statement")
    tok = tokens[pos]
    if tok.type == tKeyword and tok.value == "let":
        return parse_decl(tokens, pos, parse_expr)
    return parse_stmt(tokens, pos, parse_expr, parse_cond)


def parse_item_list_tail(tokens, pos, parse_expr, parse_cond):
    """Recursively parses top-level items until the end of input."""
    if pos >= len(tokens):
        return (), pos
    item, pos1 = parse_item(tokens, pos, parse_expr, parse_cond)
    rest, pos2 = parse_item_list_tail(tokens, pos1, parse_expr, parse_cond)
    return (item,) + rest, pos2


def parse_program(tokens, parse_expr, parse_cond):
    """
    <program> -> <item> <item_list_tail>
    Guarantees that the program is non-empty and all tokens are fully consumed.
    """
    if len(tokens) == 0:
        raise SyntaxError("SyntaxError at end of input: empty program")

    first_item, pos1 = parse_item(tokens, 0, parse_expr, parse_cond)
    rest_items, final_pos = parse_item_list_tail(tokens, pos1, parse_expr, parse_cond)

    # End of File Verification
    if final_pos < len(tokens):
        trailing_tok = tokens[final_pos]
        raise SyntaxError(
            f"SyntaxError at line {trailing_tok.line}, col {trailing_tok.column}: "
            f"unexpected token '{trailing_tok.value}'"
        )

    return make_node("Program", (first_item,) + rest_items)


def run_statement_parser(parse_expr_fn, parse_cond_fn, token_stream, error_list):
    """Entry point: skips parsing if the lexer reported errors."""
    if error_list:
        return None
    return parse_program(tuple(token_stream), parse_expr_fn, parse_cond_fn)

# ==============================================================================
# PARSER FOR EXPRESSIONS (Functional Programming Paradigm - HAZIQ)
# =============================================================================

#Expression with higher precedence 
def parse_factor(tokens, pos): 

    if pos >= len(tokens):
        raise SyntaxError("SyntaxError at end of input: expected expression")

    tok = tokens[pos]

    # Rules id --> Node("Id <name>"), id become a name
    if tok.type == tIdentifier:
        return make_node(f"Id {tok.value}"), pos + 1

    # Rules int --> Node("Int <value>"), Int become a value
    if tok.type == tInteger:   
        return make_node(f"Int {tok.value}"), pos + 1 

    # Rules ( <expr> ) --> Node("Paren <expr>") if the expression has parentheses, we look inside using parse_expr recursively
    if tok.type == tLParen:
        _, pos1 = expect(tokens, pos, tLParen, "(")
        expr_node, pos2 = parse_expr(tokens, pos1)
        _, pos3 = expect(tokens, pos2, tRParen, ")")
        return expr_node, pos3

    raise SyntaxError(
        f"SyntaxError at line {tok.line}, col {tok.column}: "
        f"unexpected token '{tok.value}' in expression"
    )

# Second Level of precedence for arithmetic operations
def parse_term(tokens, pos):

    node, current_pos = parse_factor(tokens, pos)

    while current_pos < len(tokens) and tokens[current_pos].type == tArith and tokens[current_pos].value in ("*", "/", "%"):
        op_tok = tokens[current_pos]
        right_node, next_pos = parse_factor(tokens, current_pos + 1)
        node = make_node(f"BinOp {op_tok.value}", (node, right_node))
        current_pos = next_pos

    return node, current_pos

# Third Level of precedence for arithmetic operations
def parse_expr(tokens, pos):
    node, current_pos = parse_term(tokens, pos)

    while current_pos < len(tokens) and tokens[current_pos].type == tArith and tokens[current_pos].value in ("+", "-"):
        op_tok = tokens[current_pos]
        right_node, next_pos = parse_term(tokens, current_pos + 1)
        node = make_node(f"BinOp {op_tok.value}", (node, right_node))
        current_pos = next_pos

    return node, current_pos

def parse_cond(tokens, pos):

    left_node, pos1 = parse_expr(tokens, pos)

    if pos1< len(tokens) and tokens[pos1].type == tRel:
        rel_tok = tokens[pos1]
        right_node, pos2 = parse_expr(tokens, pos1 + 1)
        return make_node(f"RelOp {rel_tok.value}", (left_node, right_node)), pos2 

    if pos1 >= len(tokens):
        raise SyntaxError("SyntaxError at end of input: expected relational operator")

    tok = tokens[pos1]
    # err_pos = pos1 if pos1 < len(tokens) else pos1 - 1
    # tok = tokens[err_pos] if err_pos < len(tokens) else None
    #if tok:
    raise SyntaxError(
        f"SyntaxError at line {tok.line}, col {tok.column}: "
        f"expected relational operator after expression"
    )

# ==============================================================================
# AST (Functional Programming Paradigm - HAZIQ)
# =============================================================================

def print_ast(node, depth=0):

    if not node:
        return

    label, children = node[0], node[1]

    print("  " * depth + str(label))
    for child in children:
        print_ast(child, depth + 1)

# ==============================================================================
# Temporary test
# =============================================================================

if __name__ == "__main__":
    import sys
    from lexer import print_token_stream, print_token_counts

    filename = "public6_syntax_end_of_input.kira"
    print(f"Reading file: {filename}...\n")

    try:
        with open(filename, "r", encoding="utf-8") as file:
            text = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{filename}'. Make sure it's in the same folder.")
        sys.exit(1)

    tokens, errors = lexer(text)
    print_token_stream(tokens)
    # print_token_counts(tokens)

    if errors:
        print("\n== LEXICAL ERRORS ==")
        for err in errors:
            print(err)
        # sys.exit(1)
    
    print_token_counts(tokens)

    if errors:
        print(f"\n{len(errors)} lexical error(s). Parsing skipped.")
        sys.exit(0)

    print("\n== AST ==")
    try:
        ast_root = run_statement_parser(parse_expr, parse_cond, tokens, errors)
        # print("\n== ABSTRACT SYNTAX TREE ==")
        print_ast(ast_root)
    except SyntaxError as e:
        print(f"\n{e}")