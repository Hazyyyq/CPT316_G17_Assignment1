# CPT316 Assignment 1: KIRA Compiler Front End
**Group:** G17  

---

## 1. Project Overview
This project implements the front-end components of the **KIRA** programming language compiler, covering:
- **Lexical Analysis (Scanner)**: Tokenizes `.kira` source files, handles whitespace and comments, and provides multi-error recovery for invalid characters or malformed tokens.
- **Syntactic Analysis (Parser)**: Recursive-descent parser that validates language grammar, enforces operator precedence, and builds the Abstract Syntax Tree (AST).
- **Driver Integration**: Command-line entry point coordinating lexical scanning and syntax parsing with clean, formatted output and zero tracebacks on errors.

---

## 2. Environment & Prerequisites
- **Language**: Python 3.10+ (tested on Python 3.11 / 3.12 / 3.15)
- **External Dependencies**: None (strictly uses Python standard library: `sys`, `os`)
- **Supported Platforms**: Windows, macOS, Linux

---

## 3. Project Directory Structure
```text
CPT316_G17_Assignment1/
├── kira.py                          # Main compiler driver entry point
├── lexer.py                         # Lexical scanner & token definitions
├── parser.py                        # Recursive-descent parser & AST builder
├── public1_arithmetic_if.kira       # Public test case 1 (arithmetic & if-else)
├── public2_while.kira               # Public test case 2 (while loop)
├── public3_nested_blocks.kira       # Public test case 3 (nested blocks & scoping)
├── public4_lexical_errors.kira      # Public test case 4 (lexical error recovery)
├── public5_syntax_error.kira        # Public test case 5 (syntax error: missing ')')
├── public6_syntax_end_of_input.kira # Public test case 6 (syntax error: missing '}')
└── README.md                        # Documentation and execution guide

## 4. Execution Guide for Evaluator

This project runs using standard Python 3 with no external dependencies (only standard library modules `sys` and `os` are required).

### Command Pattern
Open a terminal inside the project root folder (`CPT316_G17_Assignment1`) and run:

```bash
python kira.py <path_to_test_file>.kira

# Public Test 1: Arithmetic expressions, precedence & if-else
python kira.py public1_arithmetic_if.kira

# Public Test 2: While loop construct & condition evaluation
python kira.py public2_while.kira

# Public Test 3: Multi-level block scoping & nested statements
python kira.py public3_nested_blocks.kira

# Public Test 4: Multi-error recovery in scanner (parsing safely skipped)
python kira.py public4_lexical_errors.kira

# Public Test 5: Premature syntax mismatch (missing closing parenthesis)
python kira.py public5_syntax_error.kira

# Public Test 6: Incomplete program block (missing closing brace at EOF)
python kira.py public6_syntax_end_of_input.kira