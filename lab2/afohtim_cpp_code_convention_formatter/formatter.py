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
        elif content.upper() == content:
            return [content.lower()]
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
        return lexer.Token(new_token_content, lexer.TokenType.identifier, token.line(), token.column())

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
        return lexer.Token(new_token_content, lexer.TokenType.identifier, token.line(), token.column())

    def get_initial_comment(self, file_path):
        return "// {}\n".format(os.path.basename(file_path))

    def get_declaration_comment(self, type_class, type_name):
        return '/// Description for {} {}\n'.format(type_class, type_name)

    def get_type_description_comment(self, type_class, type_name):
        return '/// Description for {} {}\n'.format(type_class, type_name)

    def get_function_description_comment(self, func_name):
        return '/// Description for function {}\n'.format(type, func_name)


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

    def check_if_declaration(self, tokens, i):
        i -= 1
        res = False
        while i > 0 and tokens[i].type() == lexer.TokenType.whitespace:
            i -= 1
        if tokens[i].type() != lexer.TokenType.whitespace:
            if tokens[i].is_type() or tokens[i].type() == lexer.TokenType.identifier:
                res = True
        return res


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
        next_is_class_instance = False
        next_is_ignored = False
        class_method = False
        prev_class_name = None
        next_is_tempalte = False
        template_count = 0
        template_typenames = list()
        next_is_function_declaration = False

        while i < len(tokens) and tokens[i].content() != '}':
            content = tokens[i].content()
            if tokens[i].type() == lexer.TokenType.identifier:
                is_function = self.check_if_function(tokens, i)
                is_called = self.check_if_called(tokens, i)
                is_declaration = self.check_if_declaration(tokens, i)
                is_class = content in local_variable_dictionary['class']['names']
                is_struct = content in local_variable_dictionary['struct']['names']
                is_enum = content in local_variable_dictionary['enum']['names']
                is_macro = content in local_variable_dictionary['macro']['names']
                is_namespace = content in local_variable_dictionary['namespace']['names']

                token_type = None

                if next_is_class_instance and not is_function:
                    local_variable_dictionary['class']['variables'].append(content)
                    next_is_class_instance = False

                if next_is_ignored:
                    pass
                elif is_class:
                    token_type = IdType.Type
                    if not is_function:
                        next_is_class_instance = True
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
                    if next_is_class_instance:
                        next_is_class_instance = False
                        class_method = True
                    if content == 'main':
                        token_type = IdType.Main
                    else:
                        if is_declaration:
                            next_is_function_declaration = True
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
                        if template_count > 0:
                            template_typenames.append(content)
                        else:
                            next_class_name = content
                            class_members[content] = set()
                            local_variable_dictionary['class']['names'].append(content)
                    elif next_is_struct:
                        token_type = IdType.Type
                        if template_count > 0:
                            template_typenames.append(content)
                        else:
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
                elif content == 'class' or content == 'typename':
                    next_is_class = True
                elif content == 'struct':
                    next_is_struct = True
                elif content == 'enum':
                    next_is_enum = True
                elif content == 'namespace':
                    next_is_namespace = True
                elif content == 'template':
                    template_count += 1
                    next_is_tempalte = True
                elif tokens[i].is_type() and template_count > 0:
                    next_is_class = True
                elif content == '>' and template_count > 0:
                    template_count -= 1
                elif content == '::' and not next_is_class_instance:
                    next_is_ignored = True
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

                    next_variable_dictionary = copy.deepcopy(local_variable_dictionary)
                    if next_is_tempalte:
                        for typename in template_typenames:
                            next_variable_dictionary['class']['names'].append(typename)
                            next_is_tempalte = False

                    if current_scope['type'] == 'class' and next_scope['type'] == 'block':
                        next_scope['type'] = 'class method'
                    formatted_tokens.append(tokens[i])
                    i, formatted_scope, q, w = self.format_scope(tokens, i + 1, next_scope, next_variable_dictionary,
                                                           class_members)
                    formatted_tokens += formatted_scope
                formatted_tokens.append(tokens[i])
            i += 1
        return i, formatted_tokens, local_variable_dictionary, class_members

    def add_documentation(self, tokens, file_path):
        i = 0

        while len(tokens) > 0 and tokens[0].type() == lexer.TokenType.whitespace:
            tokens = tokens[1:]

        initial_comment = self.get_initial_comment(file_path)
        if tokens[0].content() != initial_comment:
            comment = lexer.Token(initial_comment, lexer.TokenType.comment, 0, 0)
            comment.set_error_message('No file description')
            tokens.insert(0, comment)

        comment_line = -1
        next_is_declaration = False
        type_class = None
        is_template = False
        template_count = 0
        name = str()
        indent = 0
        indent_stack = []
        while i < len(tokens):
            content = tokens[i].content()
            if content == 'template':
                comment_line = tokens[i].line()-1
                is_template = True
                template_count += 1
            elif template_count > 0:
                if content == '>':
                    template_count -= 1
            elif content == 'class':
                next_is_declaration = True
                type_class = 'class'
                indent = tokens[i].column()
            elif content == 'struct':
                next_is_declaration = True
                type_class = 'struct'
                indent = tokens[i].column()
            elif content == 'enum':
                next_is_declaration = True
                type_class = 'enum'
                indent = tokens[i].column()
            elif tokens[i].type() == lexer.TokenType.identifier:
                is_function = self.check_if_function(tokens, i)
                is_declaration = self.check_if_declaration(tokens, i)
                if next_is_declaration:
                    if not is_template:
                        comment_line = tokens[i].line()-1
                    name = tokens[i].content()
                    next_is_declaration = False
                elif is_function and is_declaration:
                    if not is_template:
                        comment_line = tokens[i].line()-1
                    type_class = 'function'
                    name = content

                    j = i
                    while tokens[j].column() > 1:
                        j -= 1
                    while tokens[j].type() == lexer.TokenType.whitespace:
                        indent_stack += [tokens[j]]
                        j += 1

            elif content in ['{', ';']:
                if name != '':
                    j = i
                    while j > 0 and tokens[j].line() > comment_line:
                        j -= 1
                    j1 = j
                    while j1 > 0 and tokens[j1].type() == lexer.TokenType.whitespace:
                        j1 -= 1
                    if tokens[j1].type() != lexer.TokenType.comment or (tokens[j1].type() == lexer.TokenType.comment and len(tokens[j1].get_error_message()) != 0):
                        declaration_comment = self.get_declaration_comment(type_class, name)
                        comment_token = lexer.Token(declaration_comment, lexer.TokenType.comment, comment_line, indent+1)
                        comment_token.set_error_message('No description of {}'.format(name))
                        tokens.insert(j + 1, comment_token)
                        for k in range(indent-1):
                            generated_token = lexer.Token(' ', lexer.TokenType.whitespace, comment_line, k)
                            tokens.insert(j + 1, generated_token)
                            i += 1
                        indent = 1
                        next_column = 1
                        for k in range(len(indent_stack)):
                            indent_content = indent_stack[k].content()
                            new_token = lexer.Token(indent_content, lexer.TokenType.whitespace, comment_line, next_column)
                            tokens.insert(j+1, new_token)
                            i += 1
                            next_column += len(indent_content)
                        indent_stack = []
                        name = ''
                        is_template = False
                        i += 1

            i += 1

    def format_file(self, file_path, format_file=False, project_formatting=False, in_file_call=False):
        with open(file_path, 'r') as file_reader:
            file = file_reader.read()
        try:
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
            self.add_documentation(formatted_tokens, file_path)
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
        except Exception as e:
            print(e)

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
