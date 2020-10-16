from lexer import Token
from lexer import TokenType
import json

def load_json():
    with open('config.json') as config:
        json_data = json.load(config)
        return json_data


def space_before_parentheses(config, previous_token):
    # TODO
    # Function declaration and Function call
    return previous_token.content() == "if" and config["Spaces"]["Before Parentheses"]["if"] or \
        previous_token.content() == "for" and config["Spaces"]["Before Parentheses"]["for"] or \
        previous_token.content() == "while" and config["Spaces"]["Before Parentheses"]["while"] or \
        previous_token.content() == "switch" and config["Spaces"]["Before Parentheses"]["switch"] or \
        previous_token.content() == "catch" and config["Spaces"]["Before Parentheses"]["catch"]


def space_around_operators(config, token):
    # TODO
    # last 2x
    return token.content() in ['=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '|=', '^=']\
           and config["Spaces"]["Around operators"]["Assignment"]\
           or token.content() in ['&&', '||'] and config["Spaces"]["Around operators"]["Logical"]\
           or token.content() in ['==', '!='] and config["Spaces"]["Around operators"]["Equality"]\
           or token.content() in ['<', '>', '<=', '>=', '<=>'] and config["Spaces"]["Around operators"]["Relational"] \
           or token.content() in ['&', '|', '^'] and config["Spaces"]["Around operators"]["Bitwise"] \
           or token.content() in ['+', '-'] and config["Spaces"]["Around operators"]["Additive"] \
           or token.content() in ['*', '/', "%"] and config["Spaces"]["Around operators"]["Multiplicative"] \
           or token.content() in ['<<', '>>'] and config["Spaces"]["Around operators"]["Shift"] \
           or token.content() in ['!', '-', '+', '++', '--'] and config["Spaces"]["Around operators"]["Unary"] \
           or token.content() in [] and config["Spaces"]["Around operators"]["-> in return type"] \
           or token.content() in ['->', '.', '->*', '.*'] and config["Spaces"]["Around operators"]["Pointer-to-member"] \



def format_file(token_list):
    config = load_json()
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
            if space_before_parentheses(config, previous_token):
                formatted_token_list.append(Token(" ", TokenType.whitespace))
                formatted_token_list.append(Token("(", TokenType.separator))
        elif token_list[i].is_operator():
            if space_around_operators(config, token_list[i]):
                formatted_token_list.append(Token(" ", TokenType.whitespace))
                formatted_token_list.append(Token(token_list[i].content(), TokenType.separator))
                formatted_token_list.append(Token(" ", TokenType.whitespace))
        else:
            formatted_token_list.append(Token(token_list[i].content(), token_list[i].get_type))

        previous_token = token_list[i]

    return formatted_token_list
