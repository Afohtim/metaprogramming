import sys, os, re
import lexer


source_file = "{project_path}/code.cpp"
assembly_file = os.path.splitext(source_file)[0] + ".s"


source_file = source_file.format(project_path='./project')
with open(source_file, 'r') as infile:
    source = infile.read().strip()


    tokens = lexer.lex(source)
    token_strings = []
    for token in tokens:
        token_strings.append(token.content())
    print(token_strings)
