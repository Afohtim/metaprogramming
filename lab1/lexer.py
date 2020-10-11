class Token:
    def __init__(self, token_string, token_type, line, symbol_pos):
        self.__token_string = token_string
        self.__token_type = token_type
        self.__line = line
        self.__symbol_pos = symbol_pos

    def type(self):
        return self.__token_type

    def content(self):
        return self.__token_string

    def is_identifier(self):
        return self.__token_type == "identifier"

    def line(self):
        return self.__line

    def char(self):
        return self.__symbol_pos


separators = ['{', '}', '(', ')', ';', ',']
single_char_operators = ['!', '~', '+', '-', '*', '/', '>', '<', '^', '%', '&', '|', '=', '?', ':', '.']
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
