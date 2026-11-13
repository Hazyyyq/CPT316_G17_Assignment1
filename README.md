# CPT316 Assignment 1: KIRA Compiler Front End
Group: G17  

---

## 1. Project Overview
This project implements the front-end components of the **KIRA** programming language compiler, covering:
- Lexical Analysis (`lexer.py`): Procedural scanner that tokenizes `.kira` source files, skips whitespace and `#` comments, tracks exact line/column positions, and provides multi-error recovery for invalid characters or malformed tokens.
- Syntactic Analysis (`parser.py`): Functional recursive-descent parser that validates language grammar, enforces operator precedence, constructs an immutable tuple-based Abstract Syntax Tree (AST), and halts cleanly on the first syntax error.
- Driver Integration & Visualization (`kira.py`): Entry point coordinating lexical scanning and syntax parsing with clean, formatted output, zero tracebacks on errors, and optional Graphviz PNG AST rendering.

---

## 2. Environment & Prerequisites
- Language: Python 3.10+ (tested on Python 3.11 / 3.12 / 3.15)
- Core Dependencies: None (strictly uses Python standard library: `sys`, `os`)
- Optional Dependency: Graphviz (for graphical PNG AST output only)
- Supported Platforms: Windows, macOS, Linux

### First-Time Device Setup (Optional: Graphical PNG AST)
To enable automatic PNG generation of the AST on a new Windows machine:
1. Open PowerShell or Terminal and run:
   ```powershell
   winget install Graphviz.Graphviz
   ```
2. Accept the installation prompt for Graphviz.
3. Install the Python `graphviz` wrapper (use `uv pip` if your Python is managed by `uv`, otherwise use `pip`):
   ```powershell
   uv pip install graphviz
   ```
4. Restart your IDE (e.g., Visual Studio Code) so it picks up the updated environment.
5. Configure System PATH: Ensure `C:\Program Files\Graphviz\bin` is added to your System `PATH` environment variable. 
(Note: `kira.py` automatically appends this default Windows path at runtime, though manual PATH configuration may be required if installed in a custom directory or on another operating system).*

> Fallback Behavior: If steps 1–5 are not configured on the host machine, the compiler will skip PNG generation without crashing and display the AST in text form only.

---

## 3. Project Directory Structure
```text
CPT316_G17_Assignment1/
├── kira.py                          # Main compiler driver & Graphviz AST visualizer
├── lexer.py                         # Lexical scanner & token definitions
├── parser.py                        # Functional recursive-descent parser & AST builder
├── public1_arithmetic_if.kira       # Public test case 1 (arithmetic & if-else)
├── public2_while.kira               # Public test case 2 (while loop)
├── public3_nested_blocks.kira       # Public test case 3 (nested blocks & scoping)
├── public4_lexical_errors.kira      # Public test case 4 (lexical error recovery)
├── public5_syntax_error.kira        # Public test case 5 (syntax error: missing ')')
├── public6_syntax_end_of_input.kira # Public test case 6 (syntax error: missing '}')
└── README.md                        # Documentation and execution guide
```

---

## 4. Execution Guide for Evaluator

The core compiler runs using standard Python 3 with no external dependencies. Open a terminal inside the project root folder (`CPT316_G17_Assignment1`) and execute the compiler using either method below.

### Option A: Command-Line Argument Mode (Recommended)
Pass the target `.kira` file path directly:
```bash
python kira.py <path_to_test_file>.kira
```
*(Depending on your OS and Python setup, `py kira.py <filename>` on Windows or `python3 kira.py <filename>` on macOS/Linux may also be used).*

#### 1. Valid Programs (Outputs: Token Stream -> Token Counts -> AST)
```bash
# Public Test 1: Arithmetic expressions, precedence & if-else
python kira.py public1_arithmetic_if.kira

# Public Test 2: While loop construct & condition evaluation
python kira.py public2_while.kira

# Public Test 3: Multi-level block scoping & nested statements
python kira.py public3_nested_blocks.kira
```

#### 2. Error Recovery & Syntax Validation
```bash
# Public Test 4: Multi-error recovery in scanner (parsing safely skipped)
python kira.py public4_lexical_errors.kira

# Public Test 5: Premature syntax mismatch (missing closing parenthesis)
python kira.py public5_syntax_error.kira

# Public Test 6: Incomplete program block (missing closing brace at EOF)
python kira.py public6_syntax_end_of_input.kira
```

### Option B: Interactive Prompt Mode
Run kira.py without any arguments and enter the filename when prompted:
```bash
python kira.py
```
```text
Enter the filename: public1_arithmetic_if.kira
```

---

## 5. Expected Output Format
- Valid Source Files: Prints `== TOKEN STREAM ==`, followed by `== TOKEN COUNTS ==`, and finally `== AST ==` (using 2 spaces per indentation level). If Graphviz is configured, an `AST.png` diagram is also generated and opened.
- Lexical Errors: Prints the token stream, lists all `LexicalError at line L, col C: ...` messages, prints `== TOKEN COUNTS ==`, and terminates cleanly without running the parser.
- **Syntax Errors**: Prints the token stream and counts, outputs the first `SyntaxError at line L, col C: ...` (or `SyntaxError at end of input: ...`), and terminates cleanly with zero Python stack traces.