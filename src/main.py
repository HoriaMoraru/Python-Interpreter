from sys import argv
from src.Interpreter import Interpreter


def main():
    if len(argv) != 2:
        return
    filename = argv[1]
    with open (filename, 'r') as file:
        input = file.read()
    Interpreter(input).interpret()


if __name__ == '__main__':
    main()
