import os
import sys
from lexer import (
    lexer, print_token_stream, print_token_counts
)
from parser import (
    run_statement_parser, parse_expr, parse_cond, print_ast
)


class customASTGraphViz:

    def __init__(self, ast_root):
        # Automatically add Graphviz to PATH on Windows if installed in default location
        if os.name == "nt" and os.path.exists(r"C:\Program Files\Graphviz\bin"):
            os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

        import graphviz  # Imported here so missing package falls back cleanly to text AST

        self.ast_root = ast_root
        self.node_count = 0
        self.graph = graphviz.Digraph(format='png')
        self.graph.attr('node', shape='rectangle')

    def add_nodes_edges(self, node):
        if node is None:
            return None

        if isinstance(node, (tuple, list)):
            label, children = node[0], node[1]
        else:
            label = str(node)
            children = []

        node_id = f"node_{self.node_count}"
        self.node_count += 1
        self.graph.node(node_id, label=str(label))

        # Add child nodes and edges recursively
        for child in children:
            if child is not None:
                child_id = self.add_nodes_edges(child)
                if child_id is not None:
                    self.graph.edge(node_id, child_id)

        return node_id

    def render_graph(self, output_filename='AST'):
        self.add_nodes_edges(self.ast_root)
        graph_output_path = self.graph.render(output_filename, view=False, cleanup=True)

        if os.path.exists(graph_output_path):
            print("\n== AST GraphViz ==")
            print(f"Graphical AST saved to: {graph_output_path}")
            if os.name == "nt":
                os.startfile(graph_output_path)  # Auto-open PNG on Windows


def main():
    # Read input filename from command line or interactive prompt
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            print(f"Error: Could not find '{filename}'.")
            sys.exit(1)
    else:
        filename = input("Enter the filename: ").strip()
        while not os.path.exists(filename):
            print(f"Error: Could not find '{filename}'.")
            filename = input("Please enter a valid filename: ").strip()

    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()

    tokens, errors = lexer(text)

    print_token_stream(tokens)

    # Report all lexical errors immediately below the stream
    if errors:
        for err in errors:
            print(err)

    print_token_counts(tokens)

    # If any lexical errors exist, parser will not run
    if errors:
        print(f"\n{len(errors)} lexical error(s). Parsing skipped.")
        sys.exit(0)
    try:
        ast_root = run_statement_parser(parse_expr, parse_cond, tokens, errors)
        print("\n== AST ==")
        print_ast(ast_root)

        try:
            ast_graph = customASTGraphViz(ast_root)
            ast_graph.render_graph()
        except Exception:
            pass  

    except SyntaxError as e:
        print(f"\n{e}")
    except Exception as e:
        print(f"\nSyntaxError: {e}")


if __name__ == "__main__":
    main()