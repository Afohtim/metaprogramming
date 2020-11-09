import sys, os, re
import lexer
import code_formatter
from code_formatter import Formatter



def get_content(token):
    return token.content()

def get_formatted_file(file_path):
    with open(file_path, 'r') as infile:
        source = infile.read()

        tokens = lexer.lex(source)

        token_strings = []
        for token in tokens:
            token_strings.append(token.content())
        #print(token_strings)

        formatter = Formatter(tokens)

        formatted = list(map(get_content, formatter.format_file()))

        ret_file = ""
        for i in formatted:
            ret_file += i

        #print(formatted)
        #for token in formatted:
        #    print(token, end='')

        return ret_file, formatter.errors
        # formatted = formatter.format_file()


if __name__ == "__main__":
    try:
        if sys.argv[1] in ['-v', '-verify']:
            if sys.argv[2] == '-p':
                print('-p is not available')
            if sys.argv[2] == '-d':
                directory_path = sys.argv[3]
                listdir = os.listdir(directory_path)
                files = [directory_path + '/' + x for x in listdir if (len(x) > 4 and x[-4:] == '.cpp') or (len(x) > 2 and x[-2:] == '.h')]
                for file_path in files:
                    print(file_path, end=' ')
                    file = open(file_path, 'r').read()
                    formatted = get_formatted_file(file_path)
                    if file == formatted:
                        print('is formatted')
                    else:
                        print('is not formatted')

            if sys.argv[2] == '-f':
                file_path = sys.argv[3]
                file = open(file_path, 'r').read()
                formatted = get_formatted_file(file_path)
                if file == formatted:
                    print('File is formatted')
                else:
                    print('File is not formatted')

        elif sys.argv[1] in ['-f', '-format']:
            if sys.argv[2] == '-p':
                print('-p is not available')
            if sys.argv[2] == '-d':
                directory_path = sys.argv[3]
                listdir = os.listdir(directory_path)
                files = [directory_path + '/' + x for x in listdir if (len(x) > 4 and x[-4:] == '.cpp') or (len(x) > 2 and x[-2:] == '.h')]
                for file_path in files:
                    print(file_path, end=' ')

                    formatted = get_formatted_file(file_path)
                    file = open(file_path, 'w').write(formatted)
                    print('has been formatted')

            if sys.argv[2] == '-f':
                file_path = sys.argv[3]
                file = open(file_path, 'r').read()
                formatted = get_formatted_file(file_path)
                print('File has been formatted')
        elif sys.argv[1] in ['-h', '-help']:
            print('use python main.py -verify -(d|f) path to verify file or folder')
            print('use python main.py -format -(d|f) path to format file or folder')
            print('-d for directories')
            print('-f for files')
            print('\'path\' variable is for path to file or folder')

        else:
            print('use -help to get help')
    except Exception:

        directory_path = './project'
        listdir = os.listdir(directory_path)
        files = [directory_path + '/' + x for x in listdir if
                 (len(x) > 4 and x[-4:] == '.cpp') or (len(x) > 2 and x[-2:] == '.h')]
        for file_path in files:
            print(file_path, end=' ')

            formatted, errors = get_formatted_file(file_path)
            print(formatted)
            print(errors)
            # file = open(file_path, 'w').write(formatted)
            print('has been formatted')



