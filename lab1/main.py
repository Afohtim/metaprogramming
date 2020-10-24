import sys, os, re
import lexer
import code_formatter
from code_formatter import Formatter


source_file = "{project_path}/main.cpp"
assembly_file = os.path.splitext(source_file)[0] + ".s"

def get_content(token):
    return token.content()

source_file = source_file.format(project_path='./project')
with open(source_file, 'r') as infile:
    source = infile.read().strip()

    tokens = lexer.lex(source)

    token_strings = []
    for token in tokens:
        token_strings.append(token.content())
    print(token_strings)

    formatter = Formatter(tokens)

    formatted = list(map(get_content, formatter.format_file()))
    #formatted = formatter.format_file()


    print(formatted)
    for token in formatted:
        print(token, end='')
