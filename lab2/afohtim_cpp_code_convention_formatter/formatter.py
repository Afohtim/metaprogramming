from afohtim_cpp_code_convention_formatter import lexer
import sys, os, re


class CodeConvectionFormatter:
    file_extensions = ['.cpp', '.h', '.hpp']

    def __init__(self):
        name_dictionary = {}
        errors = {}

    def format_identifier(self, token):
        return token

    def format_preprocessor_directive(self, token):
        return token

    def format_file(self, file_path, format_file=False):
        with open(file_path, 'r') as file_reader:
            file = file_reader.read()
        tokens = lexer.lex(file)

        formatted_tokens = []

        for token in tokens:
            if token.type() == lexer.TokenType.identifier:
                formatted_tokens.append(self.format_identifier(token))
            elif token.type() == lexer.TokenType.preprocessor_directive:
                formatted_tokens.append(self.format_preprocessor_directive(token))
            else:
                formatted_tokens.append(token)
        if format_file:
            with open(file_path, 'w') as file_writer:
                for token in formatted_tokens:
                    file_writer.write(token.content())

    @classmethod
    def is_cpp_file(cls, file_name):
        for extension in cls.file_extensions:
            if file_name.endswith(extension):
                return True

        return False

    @staticmethod
    def get_file_content(file_name):
        with open(file_name, 'r') as file:
            return file.read()

    def format_project(self, project_path, format_files=False):
        listdir = os.listdir(project_path)
        files = [project_path + '/' + x for x in listdir if self.is_cpp_file(x)]

        for file in files:
            self.format_file(file, format_files)

        directories = [project_path + '/' + x for x in listdir if os.path.isdir(project_path + '/' + x)]
        for directory in directories:
            self.format_project(directory, format_files)






