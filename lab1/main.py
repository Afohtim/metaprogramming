import sys, os, re
import lexer
import code_formatter
from code_formatter import Formatter



def get_content(token):
    return token.content()

def get_formatted_file(file_path):
    with open(file_path, 'r') as infile:
        try:
            source = infile.read()

            tokens = lexer.lex(source)

            token_strings = []
            for token in tokens:
                token_strings.append((token.content(), token.line(), token.column()))
            #print(token_strings)

            formatter = Formatter(tokens)
            formatted = list(map(get_content, formatter.format_file()))


            ret_file = ""
            for i in formatted:
                ret_file += i

            return ret_file, formatter.errors
        except Exception as e:
            return None, None


def check_if_formatted(file_path, format_file=False):
    print(file_path, end=' ')
    file = open(file_path, 'r').read()
    formatted, errors = get_formatted_file(file_path)
    if formatted is None:
        print('is not recognised')
        return
    if format_file:
        open(file_path, 'w').write(formatted)
    if not format_file:
        if file == formatted:
            print('is formatted')
        else:
            print('is not formatted')
    else:
        print('was formatted')

    with open('log.config', 'r') as log_config:
        to_log = log_config.read()
    if to_log == 'True':
        with open('errors.log', 'a+') as logs:
            logs.write(file_path)
            logs.write('\n')
            for error in errors:
                logs.write(error)
                logs.write(", ")
            logs.write('\n\n')


def check_directory_formatting(directory_path, format_files=False):
    listdir = os.listdir(directory_path)
    files = [directory_path + '/' + x for x in listdir if
             (len(x) > 4 and x[-4:] == '.cpp') or (len(x) > 2 and x[-2:] == '.h')]
    for file_path in files:
        check_if_formatted(file_path, format_files)

    directories = [directory_path + '/' + x for x in listdir if os.path.isdir(directory_path + '/' + x)]
    for directory in directories:
        check_directory_formatting(directory, format_files)


if __name__ == "__main__":
    with open('errors.log', 'w'):
        pass
    try:
        if sys.argv[1] in ['-v', '-verify']:
            if sys.argv[2] == '-p':
                directory_path = sys.argv[3]
                check_directory_formatting(directory_path)
            if sys.argv[2] == '-d':
                directory_path = sys.argv[3]
                listdir = os.listdir(directory_path)
                files = [directory_path + '/' + x for x in listdir if (len(x) > 4 and x[-4:] == '.cpp') or (len(x) > 2 and x[-2:] == '.h')]
                for file_path in files:
                    check_if_formatted(file_path)

            if sys.argv[2] == '-f':
                file_path = sys.argv[3]
                check_if_formatted(file_path)

        elif sys.argv[1] in ['-f', '-format']:
            if sys.argv[2] == '-p':
                directory_path = sys.argv[3]
                check_directory_formatting(directory_path, format_files=True)
            if sys.argv[2] == '-d':
                directory_path = sys.argv[3]
                listdir = os.listdir(directory_path)
                files = [directory_path + '/' + x for x in listdir if (len(x) > 4 and x[-4:] == '.cpp') or (len(x) > 2 and x[-2:] == '.h')]
                for file_path in files:
                    check_if_formatted(file_path, format_file=True)

            if sys.argv[2] == '-f':
                file_path = sys.argv[3]
                check_if_formatted(file_path, format_file=True)
        elif sys.argv[1] in ['-h', '-help']:
            print('use python main.py -verify -(d|f|p) path to verify file or folder')
            print('use python main.py -format -(d|f|p) path to format file or folder')
            print('use python main.py -logs -(true|false) to enable or disable logs')
            print('-d for directories')
            print('-f for files')
            print('\'path\' variable is for path to file or folder')

        elif sys.argv[1] in ['-l', '-logs']:
            with open('log.config', 'w') as log_config:
                if sys.argv[2] == 'true':
                    log_config.write('True')
                elif sys.argv[2] == 'false':
                    log_config.write('False')

        else:
            print('use -help to get help')
    except Exception:
        print('wrong usage. use -help')




