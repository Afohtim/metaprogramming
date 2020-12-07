from afohtim_cpp_code_convention_formatter import lexer
import sys, os, re
import enum
import copy


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
    Main = enum.auto()


class ScopeType(enum.Enum):
    Normal = enum.auto()
    Class = enum.auto()
    Struct = enum.auto()
    Enum = enum.auto()


class CodeConvectionFormatter:
    file_extensions = ['.cpp', '.cc', '.h', '.hpp']

    def __init__(self):
        self.name_dictionary = {'global': {}}
        self.files = dict()

    @staticmethod
    def separate_string(content):
        if '_' in content:
            snake_separation = [x.lower() for x in content.split('_')]
            while len(snake_separation[-1]) == 0:
                snake_separation = snake_separation[:-1]
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
            if i < len(separated_content) - 1 or (class_field and separated_content[i] != '_'):
                new_token_content += '_'
        return lexer.Token(new_token_content, lexer.TokenType.identifier)

    @classmethod
    def to_camel_case(cls, token, pascal_case=False, constant=False):
        separated_content = [x for x in cls.separate_string(token.content()) if x != '']
        if constant:
            if separated_content[0] != 'k':
                separated_content = ['k'] + separated_content
        new_token_content = separated_content[0]
        if pascal_case:
            new_token_content = list(new_token_content)
            new_token_content[0] = new_token_content[0].upper()
            new_token_content = ''.join(new_token_content)

        for s in separated_content[1:]:
            s = list(s)
            s[0] = s[0].upper()
            s = ''.join(s)
            new_token_content += s
        return lexer.Token(new_token_content, lexer.TokenType.identifier)

    def format_identifier(self, token, id_type=IdType.Variable):
        if id_type == IdType.Type or id_type == IdType.Enum:
            token.set_error_message('type names should be pascal case')
            return self.to_camel_case(token, pascal_case=True)
        elif id_type == IdType.ClassMember:
            token.set_error_message('class members should be snake case with underscore in the end')
            return self.to_snake_case(token, class_field=True)
        elif id_type == IdType.StructMember:
            token.set_error_message('struct members should be snake case')
            return self.to_snake_case(token)
        elif id_type == IdType.Function:
            token.set_error_message('functions should be pascal case')
            return self.to_camel_case(token, pascal_case=True)
        elif id_type == IdType.Variable:
            token.set_error_message('variables should be snake case')
            return self.to_snake_case(token)
        elif id_type == IdType.Main:
            return self.to_camel_case(token)
        elif id_type == IdType.EnumMember:
            token.set_error_message('enum members should be pascal case with k in the beginning')
            return self.to_camel_case(token, constant=True)
        elif id_type == IdType.Constant:
            token.set_error_message('constants should be pascal case with k in the beginning')
            return self.to_camel_case(token, constant=True)
        return token

    def format_preprocessor_directive(self, token):
        if token.content().endswith('.cpp"'):
            token.set_content(token.content()[:-5] + '.cc"')
        elif token.content().endswith('.hpp"'):
            token.set_content(token.content()[:-5] + '.h"')

    def get_included_file(self, preprocessor_directive):
        if preprocessor_directive.content().startswith('#include'):
            included = preprocessor_directive.content()[8:]
            while included[0].isspace():
                included = included[1:]
            while included[-1].isspace():
                included = included[:-1]
            if included[0] == '"':
                return included[1:-1]

    def check_if_function(self, tokens, i):
        i += 1
        while tokens[i].type() == lexer.TokenType.whitespace:
            i += 1
        if tokens[i].content() == '(':
            return True
        else:
            return False

    def check_if_called(self, tokens, i):
        return tokens[i - 1].content() == '.'

    def get_previous_id(self, tokens, i):
        i -= 1
        while tokens[i].type() != lexer.TokenType.identifier:
            i -= 1
        return tokens[i]

    def format_scope(self, tokens, i, current_scope, variable_dictionary, class_members):
        formatted_tokens = []
        local_variable_dictionary = copy.deepcopy(variable_dictionary)
        next_is_const = False
        next_is_class = False
        next_class_name = str()
        next_is_struct = False
        next_is_enum = False
        next_is_namespace = False
        next_is_class_member = False
        class_method = False
        prev_class_name = None
        is_main = False
        while i < len(tokens) and tokens[i].content() != '}':
            content = tokens[i].content()
            if tokens[i].type() == lexer.TokenType.identifier:
                is_function = self.check_if_function(tokens, i)
                is_called = self.check_if_called(tokens, i)
                is_class = content in local_variable_dictionary['class']['names']
                is_struct = content in local_variable_dictionary['struct']['names']
                is_enum = content in local_variable_dictionary['enum']['names']
                is_macro = content in local_variable_dictionary['macro']['names']
                is_namespace = content in local_variable_dictionary['namespace']['names']
                token_type = None

                if next_is_class_member and not is_function:
                    local_variable_dictionary['class']['variables'].append(content)
                    next_is_class_member = False

                if is_class:
                    token_type = IdType.Type
                    if not is_function:
                        next_is_class_member = True
                        prev_class_name = content
                        if content not in class_members:
                            class_members[content] = set()
                elif is_struct:
                    token_type = IdType.Type
                elif is_enum:
                    token_type = IdType.Enum
                elif is_macro:
                    token_type = IdType.Macro
                elif is_namespace:
                    token_type = IdType.Namespace
                elif is_function:
                    if next_is_class_member:
                        next_is_class_member = False
                        class_method = True
                    if content == 'main':
                        token_type = IdType.Main
                    else:
                        token_type = IdType.Function
                else:
                    if next_is_const:
                        token_type = IdType.Constant
                        next_is_const = False
                    elif next_is_enum:
                        token_type = IdType.Enum
                        local_variable_dictionary['enum']['names'].append(content)
                    elif next_is_class:
                        token_type = IdType.Type
                        next_class_name = content
                        class_members[content] = set()
                        local_variable_dictionary['class']['names'].append(content)
                    elif next_is_struct:
                        token_type = IdType.Type
                        local_variable_dictionary['struct']['names'].append(content)
                    elif next_is_namespace:
                        token_type = IdType.Namespace
                        local_variable_dictionary['namespace']['names'].append(content)
                        next_is_namespace = False
                    elif current_scope == ScopeType.Enum:
                        token_type = IdType.EnumMember
                    elif current_scope == ScopeType.Struct:
                        token_type = IdType.StructMember
                    elif current_scope == ScopeType.Class \
                        or (current_scope['type'] == 'class method' and
                            (current_scope['name'] in class_members and
                            content in class_members[current_scope['name']])):
                        token_type = IdType.ClassMember
                        class_members[current_scope['name']].add(content)
                    else:
                        if is_called:
                            previous_id = self.get_previous_id(tokens, i).content()
                            if previous_id in local_variable_dictionary['class']['names'] \
                                    or previous_id in local_variable_dictionary['class']['variables']:
                                token_type = IdType.ClassMember
                            elif previous_id in local_variable_dictionary['struct']['names']:
                                token_type = IdType.StructMember
                            elif previous_id in local_variable_dictionary['enum']['names']:
                                token_type = IdType.EnumMember
                            else:
                                token_type = IdType.Ignored
                        else:
                            if current_scope['type'] == 'class':
                                token_type = IdType.ClassMember
                                if current_scope['name'] in class_members:
                                    class_members[current_scope['name']].add(content)
                            elif current_scope['type'] == 'struct':
                                token_type = IdType.StructMember
                            elif current_scope['type'] == 'enum':
                                token_type = IdType.EnumMember
                            else:
                                token_type = IdType.Variable
                formatted_tokens.append(self.format_identifier(tokens[i], token_type))
            else:
                if tokens[i].type() == lexer.TokenType.preprocessor_directive:
                    if content.startswith('#include'):
                        included = self.get_included_file(tokens[i])
                        if included:
                            file_path = os.path.normpath(os.path.join(current_scope['name'], '..', included))
                            var_d, class_m = self.format_file(file_path, in_file_call=True)
                            local_variable_dictionary.update(var_d)
                            class_members.update(class_m)
                            self.format_preprocessor_directive(tokens[i])

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

                    next_scope = {'type': 'block', 'name': current_scope['name']}

                    if next_is_struct:
                        next_scope['type'] = 'struct'
                        next_is_struct = False
                    elif next_is_class:
                        next_scope['type'] = 'class'
                        next_scope['name'] = next_class_name
                        next_is_class = False
                    elif next_is_enum:
                        next_scope['type'] = 'enum'
                        next_is_enum = False
                    elif class_method:
                        class_method = False
                        next_scope['type'] = 'class method'
                        next_scope['name'] = prev_class_name

                    if current_scope['type'] == 'class' and next_scope['type'] == 'block':
                        next_scope['type'] = 'class'
                    formatted_tokens.append(tokens[i])
                    i, formatted_scope, q, w = self.format_scope(tokens, i + 1, next_scope, local_variable_dictionary,
                                                           class_members)
                    formatted_tokens += formatted_scope
                formatted_tokens.append(tokens[i])
            i += 1
        return i, formatted_tokens, local_variable_dictionary, class_members

    def format_file(self, file_path, format_file=False, project_formatting=False, in_file_call=False):
        with open(file_path, 'r') as file_reader:
            file = file_reader.read()
        tokens = lexer.lex(file)
        current_scope = {'type': 'file', 'name': file_path}
        empty_config = {'names': [], 'variables': []}
        variable_dictionary = {'class': copy.deepcopy(empty_config),
                               'struct': copy.deepcopy(empty_config),
                               'enum': copy.deepcopy(empty_config),
                               'macro': copy.deepcopy(empty_config),
                               'namespace': copy.deepcopy(empty_config),
                               'file_name': file_path}
        class_members = dict()
        i, formatted_tokens, variable_dictionary, class_members = self.format_scope(tokens, 0, current_scope, variable_dictionary, class_members)
        if not in_file_call:
            error_id = 1
            with open(file_path+'_verification.log', 'w') as log_writer:
                if file_path != self.normalize_name(file_path):
                    log_writer.write('{id}. {path}: wrong file extension\n'.format(id=error_id, path=file_path))
                    error_id += 1
                for i in range(len(tokens)):
                    if tokens[i].content() != formatted_tokens[i].content():
                        error_message = '{id}. {path}: line {line} - {content}: {error_message}\n'.format(
                            id=error_id, path=file_path, line = tokens[i].line(), content=tokens[i].content(),
                            error_message=tokens[i].get_error_message()
                        )
                        log_writer.write(error_message)
                        error_id += 1
        if format_file:
            if project_formatting:
                self.files[file_path] = str()
                for token in formatted_tokens:
                    self.files[file_path] += token.content()
            else:
                with open(file_path, 'w') as file_writer:
                    for token in formatted_tokens:
                        file_writer.write(token.content())
                os.rename(file_path, self.normalize_name(file_path))

        return variable_dictionary, class_members

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

    def get_all_files(self, project_path, only_folder=False):
        listdir = os.listdir(project_path)
        files = [{'path': project_path, 'name': x} for x in listdir if self.is_cpp_file(x)]
        directories = [os.path.normpath(os.path.join(project_path, x)) for x in listdir if
                       os.path.isdir(os.path.join(project_path, x))]
        if not only_folder:
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

    def normalize_name(self, file_name):
        if file_name.endswith('cpp'):
            return file_name[:-4] + '.cc'
        if file_name.endswith('hpp'):
            return file_name[:-4] + '.h'
        return file_name

    def format_project(self, project_path, format_files=False, only_folder=False):
        files = self.get_all_files(project_path, only_folder)

        for file in files:
            self.format_file(os.path.normpath(os.path.join(file['path'], file['name'])), format_files, project_formatting=True)
        for file, content in self.files.items():
            with open(file, 'w') as writer:
                writer.write(content)
        if format_files:
            for file in files:
                os.rename(os.path.normpath(os.path.join(file['path'], file['name'])), os.path.normpath(os.path.join(file['path'], self.normalize_name(file['name']))))
