import enum


class TokenType(enum.Enum):
    whitespace = 0
    separator = 1
    operator = 2
    keyword = 3
    identifier = 4
    char = 5
    string = 6
    numeric = 7


class Token:
    def __init__(self, token_string, token_type, line=None, symbol_pos=None):
        self.__token_string = token_string
        self.__token_type = token_type
        self.__line = line
        self.__symbol_pos = symbol_pos

    def type(self):
        return self.__token_type

    def content(self):
        return self.__token_string

    def is_identifier(self):
        return self.__token_type == TokenType.identifier

    def is_whitespace(self):
        return self.__token_type == TokenType.whitespace

    def is_operator(self):
        return self.__token_type == TokenType.operator

    def is_literal(self):
        return self.__token_type in [TokenType.char, TokenType.string, TokenType.numeric]

    def line(self):
        return self.__line

    def column(self):
        return self.__symbol_pos

    def get_type(self):
        return self.__token_type

    def is_type(self):
        return self.__token_string in ["auto", "bool", "char", "char8_t", "char16_t", "char32_t", "double", "float",
                                       "int", "long" "void"]


separators = ['{', '}', '(', ')', ';', ',']
operators = {'!': {'!', '!='}, '~': {'~'}, '+': {'+', '++', '+='}, '-': {'-', '--', '-=', '->', '->*'},
             '*': {'*', '*='}, '/': {'/', '/='}, '>': {'>', '>>, >=', '>>='}, '<': {'<', '<<', '<=', '<<=', '<=>'},
             '^': {'^', '^='}, '%': {'%', '%='}, '&': {'&', '&=', '&&'}, '|': {'|', '|=', '||'}, '=': {'=', '=='},
             '?': {'?'}, ':': {':', '::'}, '.': {'.', '.*'}, '[': {'[]'}, '(': {'()'}}
keywords = ["alignas", "alignof", "and", "and_eq", "asm", "atomic_cancel", "atomic_commit", "atomic_noexcept", "auto",
            "bitand", "bitor", "bool", "break", "case", "catch", "char", "char8_t", "char16_t", "char32_t", "class",
            "compl", "concept", "const", "consteval", "constexpr", "constinit", "const_cast", "continue", "co_await",
            "co_return", "co_yield", "decltype", "default", "delete", "do", "double", "dynamic_cast", "else", "enum",
            "explicit", "export", "extern", "false", "float", "for", "friend", "goto", "if", "inline", "int", "long",
            "mutable", "namespace", "new", "noexcept", "not", "not_eq", "nullptr", "operator", "or", "or_eq", "private",
            "protected", "public", "reflexpr", "register", "reinterpret_cast", "requires", "return", "short", "signed",
            "sizeof", "static", "static_assert", "static_cast", "struct", "switch", "synchronized", "template", "this",
            "thread_local", "throw", "true", "try", "typedef", "typeid", "typename", "union", "unsigned", "using",
            "virtual", "void", "volatile", "wchar_t", "while", "xor", "xor_eq"]

preprocessor_directives = ['#include', '#define', '#error', '#import', '#line', '#pragma', '#using', '#if', '#ifdef',
                           '#ifndef', '#endif', '#elif', '#else', '#undef']


def is_possible(char):
    return char.islower() or char.isupper() or char.isdigit() or char == '_'


def lex(code):
    token_list = []
    line = 1
    line_start = -1
    if code[-1] != '\n':
        code = code + '\n'
    i = 0
    while i < len(code) - 1:
        try:
            char = code[i]
            if char.isspace():
                token_list.append(Token(char, TokenType.whitespace, line, i - line_start))
                if char == '\n':
                    line += 1
                    line_start = i
            elif char in separators:
                token_list.append(Token(char, TokenType.separator, line, i - line_start))
            elif char in operators.keys():
                possible_operators = operators[char]
                operator = None
                for possible_operator in possible_operators:
                    if i + len(possible_operator) < len(code):
                        if (operator is None or len(operator) < len(possible_operator))\
                                and possible_operator == code[i:i+len(possible_operator)]:
                            operator = possible_operator
                if operator is not None:
                    i += len(operator) - 1
                    token_list.append(Token(operator, TokenType.operator, line, i))
            elif char == "'":
                char_literal = "'"
                j = i
                if code[j+1] == '\\':
                    char_literal += '\\'
                    j += 1
                char_literal += code[i+1]
                if code[j+1] != "'":
                    if code[j+2] == "'":
                        char_literal += "'"
                    else:
                        raise Exception('char literal has more than 1 character')
                token_list.append(Token(char_literal, TokenType.char, line, i - line_start))
                i = j + 2
            elif char == '"':
                j = i + 1
                string_literal = '"'
                while code[j] != '"':
                    string_literal += code[j]
                    j += 1
                string_literal += '"'
                token_list.append(Token(string_literal, TokenType.string, line, i - line_start))
                i = j
            elif is_possible(char):
                identifier = char
                j = i + 1
                while j < len(code) - 1 and (is_possible(code[j])):
                    identifier += code[j]
                    j += 1
                if identifier in keywords:
                    # add as keyword
                    token_list.append(Token(identifier, TokenType.keyword, line, i - line_start))
                else:
                    if identifier.isnumeric():
                        if j + 1 < len(code):
                            if code[j] == '.' and code[j + 1].isdigit():
                                identifier += '.'
                                j += 1
                                while j < len(code) and code[j].isdigit():
                                    identifier += code[j]
                                    j += 1
                        token_list.append(Token(identifier, TokenType.numeric, line, i - line_start))
                    else:
                        token_list.append(Token(identifier, TokenType.identifier, line, i - line_start))
                i = j - 1
            i += 1
        except Exception as e:
            print(e)
            break
    return token_list
