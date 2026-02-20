# main.py
import sys
import pathlib as pl
from src import parser

def main(args):
    if len(args) < 2:
        print("The program requires a .sc file as argument.")
        return 1

    path = pl.Path(args[1])
    if not path.exists():
        print(f"File '{path}' not found.")
        return 1
    if not args[1].endswith('.sc'):
        print(f"File '{path}' is not a .sc file.")
        return 1

    try:
        source = path.read_text()
        tokens = parser.tokenize(source)
        ast = parser.parse_sc(tokens)
        print(ast)
    except Exception as e:
        print("[ERROR]:", str(e))
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))