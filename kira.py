import sys
import os

try:
    import graphviz
except: 
    pass

from lexer import (
    lexer, print_token_stream, print_token_counts
)
from parser import (
    run_statement_parser, parse_expr, parse_cond, print_ast
)

class customASTGraphViz():

    def __init__(self, ast_root):
        self.ast_root = ast_root
        self.graph = graphviz.Digraph(format='png')
        self.graph.attr('node', shape='rectangle')

    def add_nodes_edges(self, node):
        if node is None:
            return

        if isinstance(node, (tuple, list)):
            label, children = node[0], node[1]
        else:
            label = str(node)
            children = []

        node_id = str(id(node))
        self.graph.node(node_id, label=str(label))

        # Recursively add child nodes and edges
        for child in children:
            if child is not None:
                    self.add_nodes_edges(child)
                    self.graph.edge(node_id, str(id(child)))

    def render_graph(self, output_filename='AST'):
        self.add_nodes_edges(self.ast_root)
        graph_output_path= self.graph.render(output_filename, view=False, cleanup=True)

        if os.path.exists(graph_output_path):
            os.startfile(graph_output_path)  # Open the generated graph image


def main():
    # 1. Read input filename from command line (defaults to public1 if none provided)

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            print(f"Error: Could not find '{filename}'.")
            sys.exit(1)
    else:
        filename = input("Enter the filename: ").strip()
        #filename = "public1_arithmetic_if.kira"
        while not os.path.exists(filename):
            print(f"Error: Could not find '{filename}'.")
            #sys.exit(1)
            filename = input("Please enter a valid filename: ").strip()

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
        try:
            print("\n== AST GraphViz ==")
            ast_graph = customASTGraphViz(ast_root)
            ast_graph.render_graph()
        except Exception as e:
            pass  # If GraphViz fails, only show the AST in text form

    except SyntaxError as e:
        # Catches grammar violations cleanly without a Python stack trace
        print(e)
    except Exception as e:
        # Failsafe fallback to ensure no crash or unhandled traceback
        print(f"SyntaxError: {e}")

if __name__ == "__main__":
    main()