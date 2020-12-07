import sys
from afohtim_cpp_code_convention_formatter.formatter import CodeConvectionFormatter

def main():
    try:
        if sys.argv[1] in ['-h', '-help']:
            print('use python main.py -verify -(d|f|p) path to verify file or folder')
            print('use python main.py -format -(d|f|p) path to format file or folder')
            print('use python main.py -logs -(true|false) to enable or disable logs')
            print('-d for directories')
            print('-f for files')
            print('\'path\' variable is for path to file or folder')
        else:
            if sys.argv[1] in ['-v', '-verify']:
                format_files = False
            elif sys.argv[1] in ['-f', '-format']:
                format_files = True
            else:
                raise Exception('-help')

            formatter = CodeConvectionFormatter()
            if sys.argv[2] == '-p':
                formatter.format_project(sys.argv[3], format_files)
            if sys.argv[2] == '-d':
                formatter.format_project(sys.argv[3], format_files, only_folder=True)
            if sys.argv[2] == '-f':
                formatter.format_file(sys.argv[3], format_files)
    except Exception:
        print('wrong usage. use -help')

if __name__ == '__main__':
    main()