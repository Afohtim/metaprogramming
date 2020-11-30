from afohtim_cpp_code_convention_formatter import lexer
#import lexer
import sys, os, re
import enum


class IdType(enum.Enum):
    Type = enum.auto()
    Variable = enum.auto()
    ClassMember = enum.auto()
    StructMember = enum.auto()
    Constant = enum.auto()
    Function = enum.auto()
    Namespace = enum.auto()
    Enum = enum.auto()
    EnumMember = enum.auto()
    Macro = enum.auto()
    Ignored = enum.auto()


class ScopeType(enum.Enum):
    Normal = enum.auto()
    Class = enum.auto()
    Struct = enum.auto()
    Enum = enum.auto()


class CodeConvectionFormatter:
    file_extensions = ['.cpp', '.cc', '.h', '.hpp']

    def __init__(self):
        self.name_dictionary = {'global': {}}
        errors = {}

    @staticmethod
    def separate_string(content):
        if '_' in content:
            snake_separation = [x.lower() for x in content.split('_')]
            return snake_separation
        else:
            camel_separation = []
            name_part = str()
            for c in content:
                if c.isupper() and len(name_part) > 0:
                    camel_separation.append(name_part.lower())
                    name_part = str()
                name_part += c
            camel_separation.append(name_part.lower())
            return camel_separation

    @classmethod
    def to_snake_case(cls, token, class_field=False, macro=False):
        separated_content = cls.separate_string(token.content())
        if macro:
            separated_content = [i.upper() for i in separated_content]
        new_token_content = str()
        for i in range(len(separated_content)):
            new_token_content += separated_content[i]
            if i < len(separated_content) - 1 or class_field:
                new_token_content += '_'
        return lexer.Token(new_token_content, lexer.TokenType.identifier)

    @classmethod
    def to_camel_case(cls, token, pascal_case=False, constant=False):
        separated_content = cls.separate_string(token.content())
        new_token_content = separated_content[0]
        if pascal_case:
            new_token_content = list(new_token_content)
            new_token_content[0] = new_token_content[0].upper()
            new_token_content = ''.join(new_token_content)
        if constant:
            if separated_content[0] != 'k':
                separated_content = ['k'] + separated_content
        for s in separated_content[1:]:
            s = list(s)
            s[0] = s[0].upper()
            s = ''.join(s)
            new_token_content += s
        return lexer.Token(new_token_content, lexer.TokenType.identifier)

    def format_identifier(self, token, id_type=IdType.Variable):
        if id_type in [IdType.Class, IdType.Struct]:
            return self.to_camel_case(token, pascal_case=True)
        elif id_type in IdType.ClassField:
            return self.to_snake_case(token, class_field=True)
        elif id_type in IdType.StructField:
            return self.to_snake_case(token)
        elif id_type in IdType.Function:
            return self.to_camel_case(token)
        elif id_type in IdType.Variable:
            return self.to_snake_case(token)
        return token

    def format_preprocessor_directive(self, token):
        return token

    def get_included_file(self, preprocessor_directive):
        if preprocessor_directive.content().startswith('#include'):
            included = preprocessor_directive.content()[8:]
            while included[0].isspace():
                included = included[1:]
            while included[-1].isspace():
                included = included[:-1]
            if included[0] == '"':
                return included[1:-1]

    def format_scope(self, tokens, i, current_scope, variable_dictionary):
        formatted_tokens = []
        local_variable_dictionary = variable_dictionary # {'class_names': [], 'struct_names': [], 'enum_names': []}
        next_is_const = False
        next_is_class = False
        next_is_struct = False
        next_is_enum = False
        next_is_namespace = False
        while tokens[i].content() != '}':
            content = tokens[i].content()
            if tokens[i].type == lexer.TokenType.identifier:
                is_function = self.check_if_function(tokens, i)
                is_called = self.check_if_called(tokens, i)
                is_type = content in local_variable_dictionary['class_names']+local_variable_dictionary['struct_names']
                is_enum = content in local_variable_dictionary['enum_names']
                is_macro = content in local_variable_dictionary['macro_names']
                is_namespace = content in local_variable_dictionary['namespace_names']
                token_type = None
                if is_type:
                    token_type = IdType.Type
                elif is_enum:
                    token_type = IdType.Enum
                elif is_macro:
                    token_type = IdType.Macro
                elif is_namespace:
                    token_type = IdType.Namespace
                elif is_function:
                    token_type = IdType.Function
                else:
                    if next_is_const:
                        token_type = IdType.Constant
                        next_is_const = False
                    elif next_is_enum:
                        token_type = IdType.Enum
                    elif next_is_class:
                        token_type = IdType.Type
                    elif next_is_struct:
                        token_type = IdType.Type
                    elif next_is_namespace:
                        token_type = IdType.Namespace
                    elif current_scope == ScopeType.Enum:
                        token_type = IdType.EnumMember
                    elif current_scope == ScopeType.Struct:
                        token_type = IdType.StructMember
                    elif current_scope == ScopeType.Class:
                        token_type = IdType.ClassMember
                    else:
                        if is_called:
                            previous_id = self.get_previous_id(tokens, i)
                            if previous_id in local_variable_dictionary['class_instances']:
                                token_type = IdType.ClassMember
                            elif previous_id in local_variable_dictionary['struct_instances']:
                                token_type = IdType.StructMember
                            elif previous_id in local_variable_dictionary['enum_instances']:
                                token_type = IdType.EnumMember
                            else:
                                if current_scope == 'class':
                                    token_type = IdType.ClassMember
                                elif current_scope == 'struct':
                                    token_type = IdType.StructMember
                                elif token_type == 'enum':
                                    token_type = IdType.EnumMember
                                else:
                                    token_type = IdType.Ignored
                        else:
                            token_type = IdType.Variable
                formatted_tokens.append(self.format_identifier(tokens[i], token_type))
            else:
                if content == 'const':
                    next_is_const = True
                elif content == 'class':
                    next_is_class = True
                elif content == 'struct':
                    next_is_struct = True
                elif content == 'enum':
                    next_is_enum = True
                elif content == 'namespace':
                    next_is_namespace = True
                elif content == '{':
                    # TODO recursive scope format call
                    pass
                formatted_tokens.append(tokens[i])
            i += 1

    def format_file(self, file_path, format_file=False):
        with open(file_path, 'r') as file_reader:
            file = file_reader.read()
        tokens = lexer.lex(file)

        formatted_tokens = []

        name_dictionary = {}
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type() == lexer.TokenType.identifier:
                formatted_tokens.append(self.format_identifier(token))
            elif token.type() == lexer.TokenType.preprocessor_directive:
                formatted_tokens.append(self.format_preprocessor_directive(token))
                included = self.get_included_file(token)
                if included is not None:
                    name_dictionary += self.name_dictionary[os.path.normpath(os.path.join(file_path, '..', included))]
            elif token.content() == 'class':
                while tokens[i].content() != '{':
                    if tokens[i].type() == lexer.TokenType.identifier:
                        formatted_tokens.append(self.format_identifier(token, IdType.Class))
                    i += 1
            elif token.content() == 'struct':
                while tokens[i].content() != '{':
                    if tokens[i].type() == lexer.TokenType.identifier:
                        formatted_tokens.append(self.format_identifier(token, IdType.Struct))
                    i += 1
            elif token.content() == 'namespace':
                while tokens[i].content() != ';':
                    if tokens[i].type() == lexer.TokenType.identifier:
                        formatted_tokens.append(self.format_identifier(token, IdType.Variable))
                    i += 1
            elif token.content() == 'using':
                formatted_tokens.append(token)

            else:
                formatted_tokens.append(token)
        if format_file:
            with open(file_path, 'w') as file_writer:
                for token in formatted_tokens:
                    file_writer.write(token.content())
        i += 1

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

    def get_all_files(self, project_path):
        listdir = os.listdir(project_path)
        files = [{'path': project_path, 'name': x} for x in listdir if self.is_cpp_file(x)]
        directories = [os.path.normpath(os.path.join(project_path, x)) for x in listdir if os.path.isdir(os.path.join(project_path, x))]
        for directory in directories:
            files += self.get_all_files(directory)

        return files

    def get_dependencies(self, file_name):
        dependencies = []
        with open(file_name, 'r') as file_reader:
            file = file_reader.read()
        tokens = lexer.lex(file)

        for token in tokens:
            if token.type() == lexer.TokenType.preprocessor_directive:
                if token.content().startswith('#include'):
                    included = self.get_included_file(token)
                    if included is not None:
                        dependencies.append(included)
        return dependencies

    def build_tree(self, project_path):
        files = self.get_all_files(project_path)
        referenced = dict()
        referencing = dict()
        for file in files:
            file_path = os.path.normpath(os.path.join(file['path'], file['name']))
            dependencies = self.get_dependencies(file_path)
            referencing[file] = dependencies
            for dependency in dependencies:
                referenced[os.path.normpath(os.path.join(file['path'], dependency))] = file_path
        return referenced, referencing


    def format_project(self, project_path, format_files=False):
        referenced, referencing = self.build_tree(project_path)

        file_format_queue = []

        for file_path, references in referenced.items():
            if len(references) == 0:
                file_format_queue.append(file_path)

        while len(file_format_queue) > 0:
            self.format_file(file_format_queue[0], format_files)
            file_format_queue += referencing[file_format_queue[0]]
            file_format_queue = file_format_queue[1:]






