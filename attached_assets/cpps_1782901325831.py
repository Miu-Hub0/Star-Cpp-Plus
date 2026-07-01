#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════╗
║  CP+* NATIVE - Ngôn ngữ lập trình ĐỘC LẬP       ║
║  Usage: python3 cpps.py <file.cpps>              ║
╚══════════════════════════════════════════════════╝
"""
import sys, os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexerfrom parser import Parser
from interpreter import Interpreter

def run_file(filename):
    if not os.path.exists(filename):
        print(f"❌ File không tồn tại: {filename}")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    
    print(f"📂 Đang chạy: {filename}")
    print("─" * 40)
    
    # Lex
    lexer = Lexer(source, filename)
    tokens = lexer.tokenize()
    
    # Parse
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Interpret
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    print("─" * 40)
    print("✅ Hoàn thành!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("CP+* Native Language")
        print("Usage: python3 cpps.py <file.cpps>")
        print("Example: python3 cpps.py examples/hello.cpps")
    else:
        run_file(sys.argv[1])