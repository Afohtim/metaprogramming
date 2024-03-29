from lexer import Token
from lexer import TokenType
import json


class Whitespaces:
    @staticmethod
    def space():
        return Token(' ', TokenType.whitespace)

    @staticmethod
    def eol():
        return Token('\n', TokenType.whitespace)

    @staticmethod
    def tab():
        return Token('\t', TokenType.whitespace)


class Formatter:
    def __init__(self, tokens, config_file='config.json'):
        self.i = 0
        self.whitespace_stack = []
        self.formatted_tokens = []
        self.changes = []
        self.errors = []
        self.scope_stack = []
        self.tokens = tokens
        self.config = self.load_json(config_file)
        self.types = []
        self.token_checkpoint = [self.i, self.whitespace_stack, self.formatted_tokens, self.changes, self.errors, self.scope_stack]
        self.current_class_name = None

        self.tab = None
        if self.config["Tabs and Indents"]["Use tab"]:
            self.tab = [Whitespaces.tab()]
        else:
            self.tab = [Whitespaces.space() for i in range(self.config["Tabs and Indents"]["Tab size"])]


    @staticmethod
    def load_json(config_file):
        with open(config_file) as config:
            json_data = json.load(config)
            return json_data

    @staticmethod
    def fail(s):
        print(s)
        raise Exception(s)

    def assert_token(self, token, string, forced_fail=False):
        if not forced_fail and token.content() == string:
            return True
        else:
            # TODO exception
            self.fail("expected \"{str}\" but got \"{token}\" at {line}:{char}".format(str=string, token=token.content(),
                                                                                  line=token.line(), char=token.char()))

    def assert_token_identifier(self, token):
        if token.is_identifier():
            return True
        else:
            return self.assert_token(token, "")

    def space_before_parentheses(self, current_statement_string):
        if current_statement_string in ["Function declaration", "Function call"]:
            return self.config["Spaces"]["Before Parentheses"][current_statement_string]
        # Function declaration and Function call
        return current_statement_string == "if" and self.config["Spaces"]["Before Parentheses"]["if"] or \
               current_statement_string == "for" and self.config["Spaces"]["Before Parentheses"]["for"] or \
               current_statement_string == "while" and self.config["Spaces"]["Before Parentheses"]["while"] or \
               current_statement_string == "switch" and self.config["Spaces"]["Before Parentheses"]["switch"] or \
               current_statement_string == "catch" and self.config["Spaces"]["Before Parentheses"]["catch"]

    def space_around_operators(self, current_operator):
        # TODO
        # last 2x
        return current_operator in ['=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '|=', '^='] \
               and self.config["Spaces"]["Around operators"]["Assignment"]\
               or current_operator in ['&&', '||'] and self.config["Spaces"]["Around operators"]["Logical"]\
               or current_operator in ['==', '!='] and self.config["Spaces"]["Around operators"]["Equality"]\
               or current_operator in ['<', '>', '<=', '>=', '<=>'] \
               and self.config["Spaces"]["Around operators"]["Relational"] \
               or current_operator in ['&', '|', '^'] and self.config["Spaces"]["Around operators"]["Bitwise"] \
               or current_operator in ['+', '-'] and self.config["Spaces"]["Around operators"]["Additive"] \
               or current_operator in ['*', '/', "%"] and self.config["Spaces"]["Around operators"]["Multiplicative"] \
               or current_operator in ['<<', '>>'] and self.config["Spaces"]["Around operators"]["Shift"] \
               or current_operator in ['!', '-', '+', '++', '--'] \
               and self.config["Spaces"]["Around operators"]["Unary"] \
               or current_operator in [] and self.config["Spaces"]["Around operators"]["-> in return type"] \
               or current_operator in ['->', '.', '->*', '.*'] \
               and self.config["Spaces"]["Around operators"]["Pointer-to-member"] \


    def space_before_left_brace(self, id):
        return self.config["Spaces"]["Before Left Brace"][id]

    def space_before_keywords(self, id):
        return self.config["Spaces"]["Before Keywords"][id]

    def space_within(self, current_statement):
        return self.config["Spaces"]["Within"][current_statement]

    def space_other(self, id):
        return self.config["Spaces"]["Other"][id]

    def space_in_ternary(self, id):
        return self.config["Spaces"]["In Ternary Operator"][id]

    def braces_placement(self, id):
        return self.config["Wrapping and Braces"]["Braces placement"][id]

    def space_in_template_declaration(self, id):
        return self.config["Spaces"]["In Template Declaration"][id]

    def space_in_template_instantiation(self, id):
        return self.config["Spaces"]["In Template Instantiation"][id]


    def format_file_(self, token_list):
        # deprecated
        previous_token = None
        formatted_token_list = []
        whitespace_stack = []
        for i in range(len(token_list)):
            assert (type(token_list[i]) == Token)
            if token_list[i].is_whitespace():
                whitespace_stack.append(token_list[i])
                if token_list[i].content() == '\n':
                    formatted_token_list.append(Token("\n", TokenType.whitespace))
                continue
            if token_list[i].content() == '(':
                if self.space_before_parentheses(previous_token):
                    formatted_token_list.append(Token(" ", TokenType.whitespace))
                    formatted_token_list.append(Token("(", TokenType.separator))
            elif token_list[i].is_operator():
                if self.space_around_operators(token_list[i]):
                    formatted_token_list.append(Token(" ", TokenType.whitespace))
                    formatted_token_list.append(Token(token_list[i].content(), TokenType.separator))
                    formatted_token_list.append(Token(" ", TokenType.whitespace))
            else:
                formatted_token_list.append(Token(token_list[i].content(), token_list[i].get_type))

            previous_token = token_list[i]

        return formatted_token_list

    def current_token(self):
        if self.i < len(self.tokens):
            return self.tokens[self.i]
        return Token('', TokenType.separator)

    def lookup_token(self, i=1):
        return self.tokens[self.i + i]

    def set_token_checkpoint(self):
        self.token_checkpoint = [self.i, self.whitespace_stack.copy(), self.formatted_tokens.copy(),
                                 self.changes.copy(), self.errors.copy(), self.scope_stack.copy()]

    def return_to_token_checkpoint(self):
        self.i, self.whitespace_stack, self.formatted_tokens, self.changes, self.errors, self.scope_stack = self.token_checkpoint

    def assert_current_token_content(self, content):
        if self.current_token().content() == content:
            return True
        else:
            self.fail(
                "expected \"{str}\" but got \"{token}\" at {line}:{char}"
                .format(str=content, token=self.current_token().content(), line=self.current_token().line(),
                        char=self.current_token().column()))

    def assert_current_token_type(self, type):
        if self.current_token().type() == type:
            return True
        else:
            self.fail(
                "expected \"{str}\" but got \"{token}\" at {line}:{char}"
                .format(str=type, token=self.current_token().type(), line=self.current_token().line(),
                        char=self.current_token().column()))

    def assert_current_token_is_type(self):
        if self.current_token().is_type() or self.current_token().content() in self.types:
            return True
        else:
            self.fail(
                "expected type but got \"{token}\" at {line}:{char}"
                .format(token=self.current_token().content(), line=self.current_token().line(),
                        char=self.current_token().column()))

    def save_token(self):
        self.formatted_tokens.append(self.current_token())
        self.i += 1

    def save_whitespaces(self):
        for whitespace in self.whitespace_stack:
            self.formatted_tokens.append(whitespace)
        self.whitespace_stack = []

    def skip_whitespaces(self):
        while self.current_token().is_whitespace() or self.current_token().type() == TokenType.comment \
                or self.current_token().content() in ['constexpr']:
            if self.current_token().is_whitespace():
                self.whitespace_stack.append(self.current_token())
                self.i += 1
            elif self.current_token().type() == TokenType.comment:
                self.whitespace_stack.append(self.current_token())
                self.i += 1
                self.save_whitespaces()
                '''on_new_line = True
                i = self.i
                while i > 0 and (self.tokens[i].content() != '\n' or self.tokens[i].type == TokenType.comment):
                    if self.tokens[i].is_whitespace():
                        i -= 1
                    else:
                        on_new_line = False
                if on_new_line:
                    if len(self.formatted_tokens) > 0 and len(self.whitespace_stack):
                        self.add_eol()
                    self.format_tabs(in_ws=True)
                self.save_token()
                if self.current_token().is_whitespace():
                    self.save_token()'''
            else:
                if len(self.whitespace_stack) > 0:
                    self.format_space_before_current_token(True)
                self.save_token()
                #self.format_space_after_current_token(True)

    def change_whitespaces_to_space(self):
        self.whitespace_stack = [Token(' ', TokenType.whitespace)]
        self.errors.append("expected space at {}:{}"
                           .format(self.current_token().line(),
                           self.current_token().column()))
        self.changes.append("space")

    def format_whitespaces_to_space(self):
        if not(len(self.whitespace_stack) == 1 and self.whitespace_stack[0].content() == ' '):
            self.change_whitespaces_to_space()
        self.save_whitespaces()

    def change_whitespaces_to_none(self):
        self.whitespace_stack = []
        self.errors.append("extra whitespaces at {}:{}"
                           .format(self.current_token().line(),
                           self.current_token().column()))
        self.changes.append("none")

    def format_whitespaces_to_none(self):
        if not len(self.whitespace_stack) == 0:
            self.change_whitespaces_to_none()
        self.save_whitespaces()

    def change_next_to_space(self):
        self.skip_whitespaces()
        if not self.is_one_space_on_stack():
            self.format_to_one_space()

    def format_space_before_current_token(self, is_space_needed=True):
        if is_space_needed:
            self.format_whitespaces_to_space()
        else:
            self.format_whitespaces_to_none()

    def format_space_after_current_token(self, is_space_needed=True):
        self.skip_whitespaces()
        if is_space_needed:
            self.format_whitespaces_to_space()
        else:
            self.format_whitespaces_to_none()

    def format_tabs(self, i=0, in_ws=False):
        expected_indent = self.tab * (len(self.scope_stack) + i)
        if not in_ws:
            self.skip_whitespaces()
        is_wrong = False
        if len(expected_indent) != len(self.whitespace_stack):
            is_wrong = True
        else:
            while len(self.whitespace_stack) > 0 and self.whitespace_stack[0].content() == '\n':
                self.whitespace_stack = self.whitespace_stack[1:]
            for i, j in zip(expected_indent, self.whitespace_stack):
                if i.type() != j.type():
                    is_wrong = True
                    break
        if is_wrong:
            self.errors.append("wrong indent at {}:{}"
                               .format(self.current_token().line(),
                                       self.current_token().column()))
        self.whitespace_stack = []
        self.formatted_tokens += expected_indent

    def add_eol(self):
        if self.current_token().content() == '\n':
            self.save_token()
            return
        self.skip_whitespaces()
        if len(self.whitespace_stack) > 0 and self.whitespace_stack[0].content() == '\n':
            self.formatted_tokens.append(self.whitespace_stack[0])
            self.whitespace_stack = self.whitespace_stack[1:]
        else:
            self.whitespace_stack = []
            self.formatted_tokens.append(Whitespaces.eol())
            if self.current_token().line() is None:
                pass
                #self.errors.append("expected end of line in the end of file")
            else:
                self.errors.append("expected end of line at {}:{}"
                               .format(self.current_token().line(),
                                       self.current_token().column()))

    def is_one_space_on_stack(self):
        return len(self.whitespace_stack) == 1 and self.whitespace_stack[0] == ' '

    def format_to_one_space(self):
        if not self.is_one_space_on_stack():
            self.change_whitespaces_to_space()
        self.save_whitespaces()

    def format_factor(self, expression_end=';'):
        self.skip_whitespaces()
        if self.current_token().content() == '(':
            self.save_token()
            if self.current_token().content() != ')':
                self.format_expression(')')
            self.skip_whitespaces()
            if self.current_token().content() == ',':
                self.format_space_before_current_token(self.space_other("Before comma"))
                self.save_token()
                self.format_space_after_current_token(self.space_other("After comma"))
            self.assert_current_token_content(')')
            self.save_token()
        elif self.current_token().content() == '<':
            self.format_space_before_current_token(self.space_in_template_instantiation("Before <"))
            self.save_token()
            self.skip_whitespaces()
            if self.current_token().content() == '>':
                self.format_space_before_current_token(self.space_in_template_instantiation("Within empty <>"))
            else:
                self.format_space_before_current_token(self.space_in_template_instantiation("Within <>"))
                self.format_expression('>')
                self.format_space_before_current_token(self.space_in_template_instantiation("Within <>"))
            self.save_token()
            self.skip_whitespaces()
        elif self.current_token().is_literal():
            self.save_token()
        elif self.current_token().is_identifier():
            self.format_space_before_current_token(len(self.whitespace_stack) > 0)
            self.save_token()
            self.skip_whitespaces()
            if self.current_token().content() == '(':
                self.format_space_before_current_token(self.space_before_parentheses("Function call"))
                self.format_factor()  # basically a goto
            elif self.current_token().content() in ['.', '->']:
                self.format_space_before_current_token(False)
                self.save_token()
                self.format_space_after_current_token(False)
                self.assert_current_token_type(TokenType.identifier)
                self.format_factor()
            elif self.current_token().content() == '<':
                is_template = False
                for token in self.tokens[self.i:]:
                    if token.content() == '>':
                        is_template = True
                        break
                    if token.content() in [';']:
                        break
                if is_template:
                    self.format_factor()
        elif self.current_token().content() == 'this':
            self.save_token()
            self.skip_whitespaces()
            self.assert_current_token_content('->')
            self.format_space_before_current_token(False)
            self.save_token()
            self.format_space_after_current_token(False)
            self.assert_current_token_type(TokenType.identifier)
            self.format_factor()
        else:
            self.errors.append("expected factor but got \"{}\" at Ln {}, Col {}"
                               .format(self.current_token().content(), self.current_token().line(),
                                       self.current_token().column()))

    def format_unary_expression(self, expression_end=';'):
        if self.current_token().content() in ['+', '-', '!', '~']:
            # TODO
            pass
        self.format_factor()

    def format_binary_operator(self, expression_end=';'):
        while self.current_token().is_operator() and self.current_token().content() not in [':', '?', '*']:
            token_content = self.current_token().content()
            self.format_space_before_current_token(self.space_around_operators(token_content))
            self.save_token()
            self.format_space_after_current_token(self.space_around_operators(token_content))
            self.skip_whitespaces()

    def format_conditional_expression(self, expression_end=';'):
        if self.current_token().content() == '?':
            self.format_space_before_current_token(self.space_in_ternary("Before ?"))
            self.save_token()
            self.skip_whitespaces()
            if self.current_token().content() == ':':
                self.space_in_ternary("Between")
            else:
                self.format_space_after_current_token(self.space_in_ternary("After ?"))

                self.format_expression(expression_ends=':')

                self.skip_whitespaces()
                self.assert_current_token_content(':')

                self.format_space_before_current_token(self.space_in_ternary("Before :"))
            self.save_token()
            self.format_space_after_current_token(self.space_in_ternary("After :"))
            self.format_expression(expression_end)

    def format_token(self, token, expression_end=';', enum=False, in_for=False):
        if token.is_operator() and token.content() not in [':', '?', '*']:
            self.format_binary_operator(expression_end)
        elif token.content() == '*':
            mul = True
            for token in self.formatted_tokens[::-1]:
                if token.is_whitespace():
                    continue
                if token.is_identifier():
                    mul = True
                    break
                else:
                    mul = False
                    break
            if mul:
                self.format_binary_operator(expression_end)
            else:
                self.save_token()
                self.format_space_after_current_token(self.space_other("After dereference and address-of"))

        elif self.current_token().content() == '?':
            self.format_conditional_expression(expression_end)
        elif token.content() in ['('] or token.is_identifier():
            self.format_factor(expression_end)
        elif token.content() == ',':
            self.format_space_before_current_token(self.space_other("Before comma"))
            self.save_token()
            if enum:
                self.add_eol()
                self.format_tabs()
            else:
                self.format_space_after_current_token(self.space_other("After comma"))

        else:
            self.save_whitespaces()
            self.save_token()

    def format_expression(self, expression_ends=';', enum=False, in_for=False):
        # TODO assignment
        # self.format_conditional_expression()
        if not isinstance(expression_ends, list):
            expression_ends = [expression_ends]
        min_i = 100000
        for expression_end in expression_ends:
            i = self.i
            prt_cnt = 0
            while (self.tokens[i].content() != expression_end or (expression_end == ')' and prt_cnt > 0)) and i <= min_i:
                if self.tokens[i].content() == '(':
                    prt_cnt += 1
                if self.tokens[i].content() == ')':
                    prt_cnt -= 1
                i += 1
            min_i = min(min_i, i)
        self.skip_whitespaces()
        while self.i < min_i:
            self.format_token(self.current_token(), enum=enum, in_for=in_for)
            self.skip_whitespaces()

    def format_declaration(self):
        if self.current_token().is_type() or self.current_token().content() in self.types:
            declaration_flag = True
            self.save_token()  # type
            while declaration_flag:
                declaration_flag = False
                self.skip_whitespaces()
                pointers = False
                last_pointer = None
                while self.current_token().content() in ['&', '*']:
                    if not pointers:
                        pointers = True
                        if self.current_token().content() == '*':
                            self.format_space_before_current_token(self.space_other("Before * in declaration"))
                        else:
                            self.format_space_before_current_token(self.space_other("Before & in declaration"))
                    else:
                        self.format_whitespaces_to_none()
                    self.save_token()
                    self.skip_whitespaces()
                    last_pointer = self.current_token().content()
                if pointers:
                    if last_pointer == '*':
                        self.format_space_after_current_token(self.space_other("After * in declaration"))
                    else:
                        self.format_space_after_current_token(self.space_other("After & in declaration"))

                    self.skip_whitespaces()
                self.assert_current_token_type(TokenType.identifier)
                self.save_whitespaces()  # TODO formatting?
                self.save_token()  # id
                self.skip_whitespaces()
                if self.current_token().content() not in [',', ';']:
                    # TODO formatting in declaration =
                    if self.current_token().content() == '=':
                        self.format_space_before_current_token(self.space_around_operators('='))
                        self.save_token()
                        self.format_space_after_current_token(self.space_around_operators('='))
                        self.format_expression(expression_ends=[';', ',', ':'])
                    elif self.current_token().content() == ':':
                        self.format_space_before_current_token(self.space_other("Before colon in bit field"))
                        self.save_token()
                        self.format_space_after_current_token(self.space_other("After colon in bit field"))
                        self.format_expression()
                    else:
                        self.assert_current_token_content('=')

                self.skip_whitespaces()
                if self.current_token().content() == ',':
                    # TODO formatting
                    declaration_flag = True
                    self.format_space_before_current_token(self.space_other('Before comma'))
                    self.save_token()
                    self.format_space_after_current_token(self.space_other('After comma'))
                else:
                    self.assert_current_token_content(';')
                    #self.save_whitespaces()
                    self.save_token()

    def format_if(self):
        self.save_token()

        self.skip_whitespaces()
        self.assert_current_token_content('(')
        self.format_space_before_current_token(self.space_before_parentheses('if'))
        self.save_token()

        self.skip_whitespaces()

        self.format_space_before_current_token(self.space_within('if parentheses'))
        self.format_expression(expression_ends=')')
        self.format_space_after_current_token(self.space_within('if parentheses'))

        self.assert_current_token_content(')')
        self.save_token()
        # TODO add indent
        self.scope_stack.append('if')
        self.format_statement()
        self.scope_stack.pop()
        # TODO add else

        self.skip_whitespaces()
        if self.current_token().content() == 'else':
            self.format_space_before_current_token(self.space_before_keywords("else"))
            self.scope_stack.append('else')
            self.save_token()
            self.skip_whitespaces()
            self.format_statement()
            self.scope_stack.pop()

    def format_for(self):
        self.save_token()

        self.skip_whitespaces()
        self.assert_current_token_content('(')
        self.format_space_before_current_token(self.space_before_parentheses('for'))
        self.save_token()

        self.skip_whitespaces()

        self.format_space_before_current_token(self.space_within('for parentheses'))
        self.format_expression(')', in_for=True)

        '''if self.current_token().is_type() or self.current_token().content() in self.types:
            self.format_declaration()
        else:
            self.format_expression()
        if self.current_token().content() == ':':

        else:
            self.assert_current_token_content(';')
            self.save_token()
            self.format_expression()
            self.assert_current_token_content(';')
            self.save_token()
            self.format_expression(expression_ends=')')'''

        self.format_space_after_current_token(self.space_within('for parentheses'))

        self.assert_current_token_content(')')
        self.save_token()
        # TODO add indent
        self.scope_stack.append('for')
        self.format_statement()
        self.scope_stack.pop()

    def format_while(self):
        self.save_token()

        self.skip_whitespaces()
        self.assert_current_token_content('(')
        self.format_space_before_current_token(self.space_before_parentheses('while'))
        self.save_token()

        self.skip_whitespaces()

        self.format_space_before_current_token(self.space_within('while parentheses'))
        self.format_expression(expression_ends=')')
        self.format_space_after_current_token(self.space_within('while parentheses'))

        self.assert_current_token_content(')')
        self.save_token()
        # TODO add indent
        self.scope_stack.append('while')
        self.format_statement()
        self.scope_stack.pop()

    def format_do_while(self):
        self.save_token()

        # TODO add indent
        self.scope_stack.append('do')
        self.format_statement()
        self.scope_stack.pop()

        self.skip_whitespaces()
        self.assert_current_token_content('while')
        self.format_to_one_space()  # TODO
        self.save_token()

        self.skip_whitespaces()
        self.assert_current_token_content('(')
        self.format_space_before_current_token(self.space_before_parentheses('while'))
        self.save_token()

        self.skip_whitespaces()

        self.format_space_before_current_token(self.space_within('while parentheses'))
        self.format_expression(expression_ends=')')
        self.format_space_after_current_token(self.space_within('while parentheses'))

        self.assert_current_token_content(')')
        self.save_token()

        self.assert_current_token_content(';')
        self.save_token()

    def format_switch(self):
        self.save_token()

        self.skip_whitespaces()
        self.assert_current_token_content('(')
        self.format_space_before_current_token(self.space_before_parentheses('switch'))
        self.save_token()

        self.skip_whitespaces()

        self.format_space_before_current_token(self.space_within('switch parentheses'))
        self.format_expression(expression_ends=')')
        self.format_space_after_current_token(self.space_within('switch parentheses'))

        self.assert_current_token_content(')')
        self.save_token()
        # TODO add indent
        self.scope_stack.append('switch')
        self.format_statement()
        self.scope_stack.pop()

    def format_case(self):
        self.save_token()

        self.skip_whitespaces()
        self.format_whitespaces_to_space()
        self.format_expression(expression_ends=':')
        self.skip_whitespaces()
        self.format_whitespaces_to_none()
        self.assert_current_token_content(':')
        self.save_token()

        self.scope_stack.append('case')
        self.skip_whitespaces()
        self.add_eol()
        self.format_statement()
        self.scope_stack.pop()

    def format_braces(self):
        if len(self.scope_stack) > 0 and self.scope_stack[-1] in ['if', 'else', 'for', 'while', 'do', 'switch',
                                                                  'try', 'catch']:
            current_statement = self.scope_stack[-1]
            if current_statement == 'if':
                self.format_space_before_current_token(self.space_before_left_brace('if'))
                if self.braces_placement("Other") != "End of line":
                    self.add_eol()
            elif current_statement == 'else':
                self.format_space_before_current_token(self.space_before_left_brace('else'))
                if self.braces_placement("Other") != "End of line":
                    self.add_eol()
            elif current_statement == 'for':
                self.format_space_before_current_token(self.space_before_left_brace('for'))
                if self.braces_placement("Other") != "End of line":
                    self.add_eol()
            elif current_statement == 'while':
                self.format_space_before_current_token(self.space_before_left_brace('while'))
                if self.braces_placement("Other") != "End of line":
                    self.add_eol()
            elif current_statement == 'do':
                self.format_space_before_current_token(self.space_before_left_brace('do'))
                if self.braces_placement("Other") != "End of line":
                    self.add_eol()
            elif current_statement == 'switch':
                self.format_space_before_current_token(self.space_before_left_brace('switch'))
                if self.braces_placement("Other") != "End of line":
                    self.add_eol()
            elif current_statement == 'try':
                self.format_space_before_current_token(self.space_before_left_brace('try'))
                if self.braces_placement("Other") != "End of line":
                    self.add_eol()
            elif current_statement == 'catch':
                self.format_space_before_current_token(self.space_before_left_brace('catch'))
                if self.braces_placement("Other") != "End of line":
                    self.add_eol()

            self.save_token()
            self.skip_whitespaces()
            if len(self.scope_stack) > 0 and self.scope_stack[-1] in ['if', 'for', 'do', 'switch', 'try']:
                self.scope_stack[-1] = '{'
            if self.current_token().content() == '}':
                self.save_token()
                return
            if self.braces_placement("Other") == "End of line":
                self.add_eol()
            while self.current_token().content() != '}':
                self.format_statement()
                self.skip_whitespaces()
            self.format_tabs(-1)
            self.save_token()

    def format_statement(self):
        # TODO whitespaces formatting
        self.skip_whitespaces()

        eol_needed = True
        if self.current_token().content() == 'if':
            self.format_tabs()
            self.format_if()
        elif self.current_token().content() == 'for':
            self.format_tabs()
            self.format_for()
        elif self.current_token().content() == 'while':
            self.format_tabs()
            self.format_while()
        elif self.current_token().content() == 'do':
            self.format_tabs()
            self.format_do_while()
        elif self.current_token().content() == 'switch':
            self.format_tabs()
            self.format_switch()
        elif self.current_token().content() == 'case':
            self.format_tabs()
            self.format_case()
            eol_needed = False
        elif self.current_token().content() == 'try':
            self.format_tabs()
            self.format_try_catch()
        elif self.current_token().is_type() or self.current_token().content() in self.types:
            self.format_tabs()
            self.format_declaration()
        elif self.current_token().content() == '{':
            self.format_braces()
            eol_needed = False
        else:
            if len(self.scope_stack) > 0 and self.scope_stack[-1] in ['if', 'for', 'do', 'switch', 'try']:
                self.add_eol()
            self.format_tabs()
            self.format_expression()
            self.assert_current_token_content(';')
            self.save_token()
        if eol_needed:
            self.add_eol()

    def format_function(self, is_constructor=False):
        if not is_constructor:
            # self.assert_current_token_is_type()
            if self.current_token().type() == TokenType.identifier:
                self.format_factor()
            else:
                self.save_token()
            self.format_space_after_current_token(True)
            first = True
            last = None
            while self.current_token().content() in ['*', '&']:
                if self.current_token().content() == '*':
                    if first:
                        self.format_space_before_current_token(self.space_other("Before * in declaration"))
                    self.save_token()
                    self.skip_whitespaces()
                    last = '*'
                elif self.current_token().content() == '&':
                    if first:
                        self.format_space_before_current_token(self.space_other("Before & in declaration"))
                    self.save_token()
                    self.skip_whitespaces()
                    last = '&'
            if last is not None:
                self.format_space_after_current_token(self.space_other("After {} in declaration".format(last)))
        if self.current_token().content() == 'operator':
            self.save_token()
            self.format_space_before_current_token(False)
            self.save_token()
        else:
            self.assert_current_token_type(TokenType.identifier)
            self.save_token()
        self.skip_whitespaces()
        self.assert_current_token_content('(')
        if self.space_before_parentheses('Function declaration'):
            self.format_space_after_current_token(True)
        else:
            if not len(self.whitespace_stack) == 0:
                self.change_whitespaces_to_none()
        self.save_token()
        self.skip_whitespaces()

        formatted_before_token = False
        first = True
        last = None
        if self.current_token().content() != ')':
            while self.current_token().content() != ')':
                if self.current_token().content() == ',':
                    self.format_space_before_current_token(self.space_other("Before comma"))
                    self.save_token()
                    self.format_space_after_current_token(self.space_other("After comma"))
                    formatted_before_token = True
                elif self.current_token().content() == '*':
                    if first:
                        self.format_space_before_current_token(self.space_other("Before * in declaration"))
                    self.save_token()
                    self.skip_whitespaces()
                    last = '*'
                    formatted_before_token = False
                elif self.current_token().content() == '&':
                    if first:
                        self.format_space_before_current_token(self.space_other("Before & in declaration"))
                    self.save_token()
                    self.skip_whitespaces()
                    last = '&'
                    formatted_before_token = False
                else:
                    if last is not None:
                        self.format_space_after_current_token(self.space_other("After {} in declaration".format(last)))
                        last = None
                        first = True
                    if not formatted_before_token:
                        self.format_space_before_current_token(True)
                    self.save_token()
                    self.skip_whitespaces()
                    formatted_before_token = False


            self.format_space_after_current_token(self.space_within("Function declaration parentheses"))
        else:
            self.format_space_before_current_token(self.space_within("Empty function declaration parentheses"))


        self.assert_current_token_content(')')
        self.save_token()

        self.skip_whitespaces()
        if self.current_token().content() == ';':
            self.save_token()
            return

        self.assert_current_token_content('{')
        if self.braces_placement("In functions") == "End of line":
            self.format_space_before_current_token(self.space_before_left_brace("Function"))
        else:
            self.add_eol()
            self.format_tabs()
        self.save_token()

        if self.braces_placement("In functions") == "End of line":
            self.add_eol()

        self.scope_stack.append("function")
        self.skip_whitespaces()
        while self.current_token().content() != '}':
            self.format_statement()
            self.skip_whitespaces()
        self.assert_current_token_content('}')
        self.scope_stack.pop()
        self.format_tabs()
        self.save_token()

    def format_class_statement(self):
        self.skip_whitespaces()
        if self.current_token().content() in ['public', 'private', 'protected']:
            # TODO indent
            self.format_tabs(-1)
            self.save_token()
            self.format_space_after_current_token(False)
            self.assert_current_token_content(':')
            self.save_token()
        elif self.current_token().content() == self.current_class_name:
            self.format_tabs()
            i = 1
            while self.lookup_token(i).is_whitespace():
                i += 1
            if self.lookup_token(i).content() == '(':
                self.format_function(is_constructor=True)
            else:
                self.format_declaration()
        else:
            self.format_tabs()
            self.set_token_checkpoint()
            self.assert_current_token_is_type()
            self.save_token()
            self.format_space_after_current_token(True)
            if self.current_token().content() != 'this':
                self.assert_current_token_type(TokenType.identifier)
            self.save_token()
            self.skip_whitespaces()
            if self.current_token().content() == '(':
                self.return_to_token_checkpoint()
                self.format_function()
            else:
                self.return_to_token_checkpoint()
                self.format_declaration()
        self.add_eol()

    def format_class(self):
        if self.current_token().content() in ['class', 'struct']:
            self.save_token()
            self.format_space_after_current_token(True)
            self.assert_current_token_type(TokenType.identifier)
            self.types.append(self.current_token().content())
            self.current_class_name = self.current_token().content()
            self.save_token()
            self.skip_whitespaces()
            if self.current_token().content() == ':':
                self.format_expression('{')

            self.assert_current_token_content('{')
            if self.braces_placement("In functions") == "End of line":
                self.format_space_before_current_token(self.space_before_left_brace("Class/structure"))
            else:
                self.add_eol()
                self.format_tabs()
            self.save_token()

            if self.braces_placement("In functions") == "End of line":
                self.add_eol()

            self.scope_stack.append('class')
            while self.current_token().content() != '}':
                self.format_class_statement()
                self.skip_whitespaces()
                #self.save_whitespaces()
            self.save_token()
            self.assert_current_token_content(';')
            self.save_token()
            self.scope_stack.pop()
            self.current_class_name = None

    def format_enum(self):
        self.save_token()
        self.skip_whitespaces()
        if self.current_token().content() == 'class':
            self.format_space_before_current_token(True)
            self.save_token()
            self.format_space_after_current_token(True)
            self.assert_current_token_type(TokenType.identifier)
            self.types.append(self.current_token().content())
            self.current_class_name = self.current_token().content()
            self.save_token()
            self.skip_whitespaces()
            if self.current_token().content() == ':':
                self.format_expression('{')
        else:
            self.format_space_after_current_token(True)
            self.assert_current_token_type(TokenType.identifier)
            self.types.append(self.current_token().content())
            self.current_class_name = self.current_token().content()
            self.save_token()
            self.skip_whitespaces()
            if self.current_token().content() == ':':
                self.format_expression('{')
        self.assert_current_token_content('{')
        self.format_space_before_current_token(self.space_before_left_brace("Class/structure"))
        self.save_token()

        self.scope_stack.append("enum")
        self.add_eol()
        self.format_tabs()
        self.skip_whitespaces()
        self.format_expression('}', enum=True)
        self.scope_stack.pop()

        self.skip_whitespaces()
        self.assert_current_token_content('}')
        self.add_eol()
        self.save_token()
        self.assert_current_token_content(';')
        self.save_token()

    def format_template(self):
        self.assert_current_token_content('template')
        self.save_token()
        self.skip_whitespaces()
        self.assert_current_token_content('<')
        self.format_space_before_current_token(self.space_in_template_declaration("Before <"))
        self.save_token()
        self.skip_whitespaces()
        if self.current_token().content() == '>':
            self.format_space_before_current_token(self.space_in_template_declaration("Within empty <>"))
            self.save_token()
        else:
            self.format_space_before_current_token(self.space_in_template_declaration("Within <>"))
            while self.current_token().content() != '>':
                if self.current_token().content() not in ['class', 'typename']:
                    self.fail('wrong arguments in template declaration in {}:{}'.format(self.current_token().line(),
                                                                                        self.current_token().column()))
                self.save_token()
                self.skip_whitespaces()
                self.assert_current_token_type(TokenType.identifier)
                self.format_space_before_current_token(True)
                self.save_token()
                self.skip_whitespaces()
                if self.current_token().content() == ',':
                    self.format_space_before_current_token(self.space_other("Before comma"))
                    self.save_token()
                    self.format_space_after_current_token(self.space_other("After comma"))
            self.format_space_before_current_token(self.space_in_template_declaration("Within <>"))
            self.save_token()
            self.skip_whitespaces()
            self.add_eol()
            if self.current_token().is_type() or self.current_token().type() == TokenType.identifier:
                self.format_function()
            elif self.current_token().content() == 'class':
                self.format_class()



    def format_file(self):
        first = True
        while self.i < len(self.tokens):
            if not first and self.current_token().type() != TokenType.preprocessor_directive:
                self.add_eol()
            first = False
            self.skip_whitespaces()
            #self.save_whitespaces()
            if self.current_token().is_type() or self.current_token().type() == TokenType.identifier:
                self.format_function()
            elif self.current_token().content() in ['class', 'struct']:
                self.format_class()
            elif self.current_token().content() == 'enum':
                self.format_enum()
            elif self.current_token().type() == TokenType.preprocessor_directive:
                self.save_token()
            elif self.current_token().content() == 'template':
                self.format_template()
            else:
                self.fail("expected class or function at {}:{}".format(self.current_token().line(), self.current_token().column()))
            self.add_eol()
        return self.formatted_tokens




