from lexer import Token
from lexer import TokenType
import json


class Formatter:
    def __init__(self, tokens, config_file='config.json'):
        self.i = 0
        self.whitespace_stack = []
        self.formatted_tokens = []
        self.changes = []
        self.errors = []
        self.scope_stack = ["program"]
        self.tokens = tokens
        self.config = self.load_json(config_file)
        self.types = []
        self.token_checkpoint = [self.i, self.whitespace_stack, self.formatted_tokens, self.changes, self.errors, self.scope_stack]
        self.current_class_name = None

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
        # TODO
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

    def space_within(self, current_statement):
        return self.config["Spaces"]["Within"][current_statement]

    def space_other(self, id):
        return self.config["Spaces"]["Other"][id]

    def space_in_ternary(self, id):
        return self.config["Spaces"]["In Ternary Operator"][id]

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
        return self.tokens[self.i]

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
        while self.current_token().is_whitespace():
            self.whitespace_stack.append(self.current_token())
            self.i += 1

    def change_whitespaces_to_space(self):
        self.whitespace_stack = [Token(' ', TokenType.whitespace)]
        # TODO push to changes
        self.changes.append("space")

    def format_whitespaces_to_space(self):
        self.change_whitespaces_to_space()
        self.save_whitespaces()

    def change_whitespaces_to_none(self):
        self.whitespace_stack = []
        # TODO push to changes
        self.changes.append("none")

    def format_whitespaces_to_none(self):
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

    def is_one_space_on_stack(self):
        return len(self.whitespace_stack) == 1 and self.whitespace_stack[0] == ' '

    def format_to_one_space(self):
        if not self.is_one_space_on_stack():
            self.change_whitespaces_to_space()
        self.save_whitespaces()

    def format_factor(self):
        #self.skip_whitespaces()
        if self.current_token().content() == '(':
            self.save_token()
            if self.current_token().content() != ')':
                self.format_expression()
            self.skip_whitespaces()
            if self.current_token().content() == ',':
                self.format_space_before_current_token(self.space_other("Before comma"))
                self.save_token()
                self.format_space_after_current_token(self.space_other("After comma"))
            self.assert_current_token_content(')')
            self.save_token()
        elif self.current_token().is_literal():
            self.save_token()
        elif self.current_token().is_identifier():
            self.save_token()
            self.skip_whitespaces()
            if self.current_token().content() == '(':
                self.format_space_before_current_token(self.space_before_parentheses("Function call"))
                self.format_factor()  # basically a goto
            elif self.current_token().content() == '.':
                self.format_space_before_current_token(False)
                self.save_token()
                self.format_space_after_current_token(False)
                self.assert_current_token_type(TokenType.identifier)
                self.format_factor()
        elif self.current_token().content() == 'this':
            self.save_token()
            self.skip_whitespaces()
            self.assert_current_token_content('.')
            self.format_space_before_current_token(False)
            self.save_token()
            self.format_space_after_current_token(False)
            self.assert_current_token_type(TokenType.identifier)
            self.format_factor()
        else:
            self.errors.append("expected factor but got \"{}\" at Ln {}, Col {}"
                               .format(self.current_token().content(),self.current_token().line(),
                                       self.current_token().column()))

    def format_unary_expression(self):
        if self.current_token().content() in ['+', '-', '!', '~']:
            # TODO
            pass
        self.format_factor()

    def format_binary_operator(self):
        self.format_unary_expression()
        self.skip_whitespaces()
        while self.current_token().is_operator() and self.current_token().content() not in [':', '?']:
            if self.space_around_operators(self.current_token().content()):
                self.format_to_one_space()
                self.save_token()
                self.skip_whitespaces()
                self.format_to_one_space()
            else:
                # TODO
                pass
            self.format_unary_expression()
            self.skip_whitespaces()

    def format_conditional_expression(self):
        self.format_binary_operator()
        self.skip_whitespaces()
        if self.current_token().content() == '?':
            self.format_space_before_current_token(self.space_in_ternary("Before ?"))
            self.save_token()
            self.skip_whitespaces()
            if self.current_token().content() == ':':
                self.space_in_ternary("Between")
            else:
                self.format_space_after_current_token(self.space_in_ternary("After ?"))

                self.format_expression()

                self.skip_whitespaces()
                self.assert_current_token_content(':')

                self.format_space_before_current_token(self.space_in_ternary("Before :"))
            self.save_token()
            self.format_space_after_current_token(self.space_in_ternary("After :"))
            self.format_expression()


    def format_expression(self):
        # TODO assignment
        self.format_conditional_expression()

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
                        self.format_expression()
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
                    self.save_whitespaces()
                    self.save_token()

    def format_if(self):
        self.save_token()

        self.skip_whitespaces()
        self.assert_current_token_content('(')
        self.format_space_before_current_token(self.space_before_parentheses('if'))
        self.save_token()

        self.skip_whitespaces()

        self.format_space_before_current_token(self.space_within('if parentheses'))
        self.format_expression()
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
            self.scope_stack.append('else')
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
        # TODO for conditions
        if self.current_token().is_type() or self.current_token().content() in self.types:
            self.format_declaration()
        else:
            self.format_expression()
        self.assert_current_token_content(';')
        self.save_token()
        self.format_expression()
        self.assert_current_token_content(';')
        self.save_token()
        self.format_expression()

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
        self.format_expression()
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

        self.assert_current_token_content('(')
        self.format_space_before_current_token(self.space_before_parentheses('while'))
        self.save_token()

        self.skip_whitespaces()

        self.format_space_before_current_token(self.space_within('while parentheses'))
        self.format_expression()
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
        self.format_expression()
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
        self.format_expression()
        self.skip_whitespaces()
        self.format_whitespaces_to_none()
        self.assert_current_token_content(':')
        self.save_token()

        self.scope_stack.append('case')
        self.format_statement()
        self.scope_stack.pop()

    def format_braces(self):
        if len(self.scope_stack) > 0 and self.scope_stack[-1] in ['if', 'else', 'for', 'while', 'do', 'switch',
                                                                  'try', 'catch']:
            current_statement = self.scope_stack[-1]
            if current_statement == 'if':
                self.format_space_before_current_token(self.space_before_left_brace('if'))
            elif current_statement == 'else':
                self.format_space_before_current_token(self.space_before_left_brace('else'))
            elif current_statement == 'for':
                self.format_space_before_current_token(self.space_before_left_brace('for'))
            elif current_statement == 'while':
                self.format_space_before_current_token(self.space_before_left_brace('while'))
            elif current_statement == 'do':
                self.format_space_before_current_token(self.space_before_left_brace('do'))
            elif current_statement == 'switch':
                self.format_space_before_current_token(self.space_before_left_brace('switch'))
            elif current_statement == 'try':
                self.format_space_before_current_token(self.space_before_left_brace('try'))
            elif current_statement == 'catch':
                self.format_space_before_current_token(self.space_before_left_brace('catch'))
            self.save_token()
            self.skip_whitespaces()
            while self.current_token().content() != '}':
                self.format_statement()
                self.skip_whitespaces()
            self.save_whitespaces()
            self.save_token()

    def format_statement(self):
        # TODO whitespaces formatting
        self.skip_whitespaces()

        if self.current_token().content() == 'if':
            self.save_whitespaces()
            self.format_if()
        elif self.current_token().content() == 'for':
            self.save_whitespaces()
            self.format_for()
        elif self.current_token().content() == 'while':
            self.save_whitespaces()
            self.format_while()
        elif self.current_token().content() == 'do':
            self.save_whitespaces()
            self.format_do_while()
        elif self.current_token().content() == 'switch':
            self.save_whitespaces()
            self.format_switch()
        elif self.current_token().content() == 'case':
            self.save_whitespaces()
            self.format_case()
        elif self.current_token().content() == 'try':
            self.save_whitespaces()
            self.format_try_catch()
        elif self.current_token().is_type() or self.current_token().content() in self.types:
            self.save_whitespaces()
            self.format_declaration()
        elif self.current_token().content() == '{':
            self.format_braces()
        else:
            self.save_whitespaces()
            self.format_expression()
            self.assert_current_token_content(';')
            self.save_token()

        pass

    def format_function(self, is_contructor=False):
        if not is_contructor:
            self.assert_current_token_is_type()
            self.save_token()
            self.change_next_to_space()
        self.assert_current_token_type(TokenType.identifier)
        self.save_token()
        self.skip_whitespaces()
        self.assert_current_token_content('(')
        if self.space_before_parentheses('Function declaration'):
            self.format_to_one_space()
        else:
            if not len(self.whitespace_stack) == 0:
                self.change_whitespaces_to_none()
        self.save_token()
        self.skip_whitespaces()

        if self.current_token().content() != ')':
            arguments_count = 0
            argument_expected = True
            self.format_space_before_current_token(self.space_within("Function declaration parentheses"))
            while argument_expected:
                arguments_count += 1
                argument_expected = False
                self.assert_current_token_is_type()
                self.save_token()
                self.format_space_after_current_token(True)
                self.assert_current_token_type(TokenType.identifier)
                self.save_token()
                self.skip_whitespaces()
                if self.current_token().content() == ',':
                    self.format_space_before_current_token(self.space_other("Before comma"))
                    argument_expected = True
                    self.save_token()
                    self.format_space_after_current_token(self.space_other("After comma"))
            self.format_space_after_current_token(self.space_within("Function declaration parentheses"))



        self.assert_current_token_content(')')
        if self.space_within("Empty function declaration parentheses"):
            self.format_to_one_space()
        else:
            if not len(self.whitespace_stack) == 0:
                self.change_whitespaces_to_none()
        self.save_token()

        # TODO formatting here
        self.skip_whitespaces()
        self.save_whitespaces()

        self.scope_stack.append("function")
        self.assert_current_token_content('{')
        self.save_token()

        while self.current_token().content() != '}':
            self.format_statement()
            self.skip_whitespaces()
        self.assert_current_token_content('}')
        self.save_whitespaces()
        self.save_token()
        self.scope_stack.pop()

    def format_class_statement(self):
        self.skip_whitespaces()
        self.save_whitespaces()
        if self.current_token().content() in ['public', 'private', 'protected']:
            # TODO indent
            self.save_token()
            self.format_space_after_current_token(False)
            self.assert_current_token_content(':')
            self.save_token()
        elif self.current_token().content() == self.current_class_name:
            i = 1
            while self.lookup_token(i).is_whitespace():
                i += 1
            if self.lookup_token(i).content() == '(':
                self.format_function(is_contructor=True)
            else:
                self.format_declaration()
        else:
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

    def format_class(self):
        if self.current_token().content() in ['class', 'struct']:
            self.save_token()
            self.format_space_after_current_token(True)
            self.assert_current_token_type(TokenType.identifier)
            self.types.append(self.current_token().content())
            self.current_class_name = self.current_token().content()
            self.save_token()
            self.format_space_after_current_token(self.space_before_left_brace("Class/structure"))
            self.assert_current_token_content('{')
            self.save_token()

            self.scope_stack.append('class')
            while self.current_token().content() != '}':
                self.format_class_statement()
                self.skip_whitespaces()
                self.save_whitespaces()
            self.save_token()
            self.assert_current_token_content(';')
            self.save_token()
            self.scope_stack.pop()
            self.current_class_name = None

    def format_file(self):
        while self.i < len(self.tokens):
            self.skip_whitespaces()
            self.save_whitespaces()
            if self.current_token().is_type() or self.current_token().content() in self.types:
                self.format_function()
            elif self.current_token().content() in ['class', 'struct']:
                self.format_class()
            else:
                self.fail("expected class or function at {}:{}".format(self.current_token().line(), self.current_token().column()))
        return self.formatted_tokens


