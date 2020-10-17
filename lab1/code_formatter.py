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

    @staticmethod
    def token_is_type(token):
        if token.content() in ["int"]:
            return True

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
        return current_operator in ['=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '|=', '^='] and self.config["Spaces"]["Around operators"]["Assignment"]\
               or current_operator in ['&&', '||'] and self.config["Spaces"]["Around operators"]["Logical"]\
               or current_operator in ['==', '!='] and self.config["Spaces"]["Around operators"]["Equality"]\
               or current_operator in ['<', '>', '<=', '>=', '<=>'] and self.config["Spaces"]["Around operators"]["Relational"] \
               or current_operator in ['&', '|', '^'] and self.config["Spaces"]["Around operators"]["Bitwise"] \
               or current_operator in ['+', '-'] and self.config["Spaces"]["Around operators"]["Additive"] \
               or current_operator in ['*', '/', "%"] and self.config["Spaces"]["Around operators"]["Multiplicative"] \
               or current_operator in ['<<', '>>'] and self.config["Spaces"]["Around operators"]["Shift"] \
               or current_operator in ['!', '-', '+', '++', '--'] and self.config["Spaces"]["Around operators"]["Unary"] \
               or current_operator in [] and self.config["Spaces"]["Around operators"]["-> in return type"] \
               or current_operator in ['->', '.', '->*', '.*'] and self.config["Spaces"]["Around operators"]["Pointer-to-member"] \


    def space_within(self, current_statement):
        return self.config["Spaces"]["Within"][current_statement]

    def format_file_(self, token_list):
        config = self.load_json()
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

    def change_whitespaces_to_none(self):
        self.whitespace_stack = []
        # TODO push to changes
        self.changes.append("none")

    def change_next_to_space(self):
        self.skip_whitespaces()
        if not self.is_one_space_on_stack():
            self.format_to_one_space()

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
            self.format_expression()
            self.assert_current_token_content(')')
            self.save_token()
        elif self.current_token().content().isnumeric() or self.current_token().is_identifier():
            self.save_token()
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
        while self.current_token().is_operator():
            if self.space_around_operators(self.current_token().content()):
                self.format_to_one_space()
                self.save_token()
                self.skip_whitespaces()
                self.format_to_one_space()
            else:
                # TODO
                pass
            self.format_unary_expression()

    def format_conditional_expression(self):
        self.format_binary_operator()

    def format_expression(self):
        if self.current_token().is_identifier():
            pass
        else:
            self.format_conditional_expression()

    def format_declaration(self):
        # TODO
        if self.current_token().is_type():
            self.save_token()

    def format_if(self):
        self.format_if()
        self.save_token()

        self.skip_whitespaces()
        self.assert_current_token_content('(')
        if self.space_before_parentheses('if'):
            self.format_to_one_space()
            self.save_token()
        else:
            if not len(self.whitespace_stack) == 0:
                self.change_whitespaces_to_none()

        self.skip_whitespaces()
        if self.space_within('if parentheses'):
            self.format_to_one_space()
            self.format_expression()
            self.format_to_one_space()

        self.assert_current_token_content(')')
        self.save_token()
        # TODO add indent
        self.scope_stack.append('if')
        self.format_statement()
        self.scope_stack.pop()
        # TODO add else

    def format_statement(self):
        # TODO whitespaces formatting
        self.skip_whitespaces()
        self.save_whitespaces()

        if self.current_token().content() == 'if':
            self.format_if()
        elif self.current_token().content() == 'for':
            self.format_for()
        elif self.current_token().content() == 'while':
            self.format_while()
        elif self.current_token().content() == 'do':
            self.format_do_while()
        elif self.current_token().content() == 'switch':
            self.format_switch()
        elif self.current_token().content() == 'try':
            self.format_try_catch()
        elif self.current_token().is_type():
            self.format_declaration()
        else:
            self.format_expression()
            self.assert_current_token_content(';')
            self.save_token()

        pass

    def format_function(self):
        if self.current_token().is_type():
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

            self.assert_current_token_content('{')
            self.save_token()

            while self.current_token().content() != '}':
                self.format_statement()
                self.skip_whitespaces()
            self.assert_current_token_content('}')
            self.save_whitespaces()
            self.save_token()

    def format_file(self):
        self.skip_whitespaces()
        self.save_whitespaces()
        self.format_function()
        return self.formatted_tokens


