#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  CP+* (C-Plus-Plus-Star) Language — Native Interpreter       ║
║  Usage: python3 cpps.py <file.cpps>                          ║
║  Version: 2.0 — Advanced Edition                             ║
╚══════════════════════════════════════════════════════════════╝
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, CPPSPanic, CPPSError


def run_file(filename, verbose=False):
    if not os.path.exists(filename):
        print(f"❌ File không tồn tại: {filename}")
        sys.exit(1)

    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    print(f"📂 Đang chạy: {filename}")
    print("─" * 50)

    try:
        # Lexer
        lexer = Lexer(source, filename)
        tokens = lexer.tokenize()

        if verbose:
            print(f"[DEBUG] Tokens: {len(tokens)}")

        # Parser
        parser = Parser(tokens)
        ast = parser.parse()

        if verbose:
            print(f"[DEBUG] AST statements: {len(ast.statements)}")

        # Interpreter
        interp = Interpreter()
        interp.execute(ast)

    except LexerError as e:
        print(f"\n❌ Lexer Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print(f"\n❌ Parse Error: {e}", file=sys.stderr)
        sys.exit(1)
    except CPPSPanic as e:
        print(f"\n💥 PANIC: {e.msg}", file=sys.stderr)
        sys.exit(1)
    except CPPSError as e:
        print(f"\n❌ Runtime Error: {e.msg}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(0)

    print("─" * 50)
    print("✅ Hoàn thành!")


def run_repl():
    """Interactive REPL mode"""
    print("╔══════════════════════════════════════════════════════╗")
    print("║  CP+* Interactive REPL — type 'exit' to quit         ║")
    print("╚══════════════════════════════════════════════════════╝")
    interp = Interpreter()
    buf = []
    depth = 0
    while True:
        try:
            prompt = ">>> " if depth == 0 else "... "
            line = input(prompt)
            if line.strip() in ('exit', 'quit'):
                break
            buf.append(line)
            depth += line.count('{') - line.count('}')
            if depth <= 0:
                source = '\n'.join(buf)
                buf = []
                depth = 0
                if not source.strip():
                    continue
                try:
                    from lexer import Lexer
                    from parser import Parser
                    tokens = Lexer(source, "<repl>").tokenize()
                    ast = Parser(tokens).parse()
                    interp.execute(ast)
                except Exception as e:
                    print(f"Error: {e}")
        except (EOFError, KeyboardInterrupt):
            break
    print("Bye!")


def print_help():
    print("""CP+* (C-Plus-Plus-Star) Language Interpreter v2.0

Usage:
  python3 cpps.py <file.cpps>          Run a CP+* source file
  python3 cpps.py --repl               Start interactive REPL
  python3 cpps.py --verbose <file>     Run with debug output
  python3 cpps.py --help               Show this help

Examples:
  python3 cpps.py examples/hello.cpps
  python3 cpps.py examples/ultimate_test.cpps
  python3 cpps.py examples/full_oop.cpps
""")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or '--help' in args or '-h' in args:
        if not args:
            print_help()
            print("\nRunning demo: examples/hello.cpps")
            print()
            run_file("examples/hello.cpps")
        else:
            print_help()
    elif '--repl' in args:
        run_repl()
    elif '--verbose' in args:
        idx = args.index('--verbose')
        filename = args[idx + 1] if idx + 1 < len(args) else None
        if filename:
            run_file(filename, verbose=True)
        else:
            print("❌ Cần cung cấp tên file sau --verbose")
    else:
        run_file(args[0])
