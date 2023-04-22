#!/usr/bin/env python3.11
import copy
import json
import os.path
import subprocess
import time
from typing import List, Optional, Tuple, Dict
import sys

STATIC_MEMORY_SIZE = 1024 * 1024 * 8
MAX_ARGS = 5

strings = list()
string_length = 0

debug = False
if 'DEBUG' in os.environ:
    debug = True

info_cmd = True
if 'NO_CMD_INFO' in os.environ:
    info_cmd = False

info = True
if 'NOINFO' in os.environ:
    info = False

fasm_loc = 'fasm'
if 'FASM_LOC' in os.environ:
    fasm_loc = os.environ['FASM_LOC']


def shift_args(args: List) -> Tuple[str, List]:
    return args[0], args[1:]


def usage(program_name: str) -> None:
    print(f"{program_name} <input file> <output file>")


def todo():
    assert False, "Not implemented yet"


auto_ = 0


def auto(reset=False):
    global auto_
    if reset:
        auto_ = 0
    val = auto_
    auto_ += 1
    return val


class TokenType(int):
    COMMA = auto()
    OPEN_CURLY_BRACKET = auto()
    CLOSE_CURLY_BRACKET = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    MULT = auto()
    SEMICOLON = auto()
    ADD = auto()
    MINUS = auto()
    ASSIGN = auto()
    IDENTIFIER = auto()
    INT = auto()
    STRING = auto()
    FUNCTION = auto()
    PUTC = auto()
    NEQ = auto()
    EQ = auto()
    WHILE = auto()
    IF = auto()
    LET = auto()
    TokenType_NUMBERS = auto()


class Location:
    def __init__(self, line, col, file):
        self.line = line
        self.col = col
        self.file = file

    def __str__(self):
        return f"{self.file}:{self.line}:{self.col}"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return dict(
            line=self.line,
            col=self.col,
            file=self.file,
        )


class Token:
    def __init__(self, literal, type_, location):
        self.literal = literal
        self.type = type_
        self.location = location

    def __str__(self):
        return f"Token[literal=`{self.literal}`, type={self.type}, location={self.location}"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        location = self.location.to_dict()
        return dict(
            literal=self.literal,
            type=self.type,
            location=location,
        )


class Lexer:
    def __init__(self, input_file: str, program_string: str):
        self.program_string = program_string
        self.cursor = 0
        self.line = 1
        self.cursor_on_line = 1
        self.input_file = input_file

    def chop_char(self) -> str:
        char = self.program_string[self.cursor]
        self.cursor += 1
        self.cursor_on_line += 1
        return char

    def __iter__(self):
        return self

    def trim_left(self):
        while self.program_string[self.cursor].isspace():
            char = self.chop_char()
            if self.cursor >= len(self.program_string):
                raise StopIteration
            if char == '\n':
                self.line += 1
                self.cursor_on_line = 1

    def __next__(self):
        assert TokenType.TokenType_NUMBERS == 22
        if self.cursor >= len(self.program_string):
            raise StopIteration
        self.trim_left()

        cursor = self.cursor
        location = Location(self.line, self.cursor_on_line, self.input_file)
        if self.program_string[cursor] == '"':
            literal = ""
            self.chop_char()
            while self.program_string[self.cursor] != '"':
                char = self.chop_char()
                if char == '\\':
                    escape = self.chop_char()
                    if escape == 'n':
                        char = '\n'
                literal += char
            self.chop_char()
            type_ = TokenType.STRING
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == "'":
            self.chop_char()
            literal = ord(self.chop_char())
            self.chop_char()
            type_ = TokenType.INT
            return Token(literal, type_, location)
        elif self.program_string[self.cursor].isalpha() or self.program_string[self.cursor] == '_':
            while self.program_string[self.cursor].isalnum() or self.program_string[self.cursor] == '_':
                self.chop_char()
            literal = self.program_string[cursor:self.cursor]
            type_ = TokenType.IDENTIFIER
            if literal == 'putc':
                type_ = TokenType.PUTC
            elif literal == 'if':
                type_ = TokenType.IF
            elif literal == 'while':
                type_ = TokenType.WHILE
            elif literal == 'fun':
                type_ = TokenType.FUNCTION
            elif literal == 'let':
                type_ = TokenType.LET
            return Token(literal, type_, location)
        elif self.program_string[self.cursor].isnumeric():
            while self.program_string[self.cursor].isalnum() or self.program_string[self.cursor] == '_':
                self.chop_char()
            literal = self.program_string[cursor:self.cursor]
            type_ = TokenType.INT
            return Token(literal, type_, location)

        elif self.program_string[self.cursor] == '!':
            self.chop_char()
            if self.program_string[self.cursor] == '=':
                literal = "!" + self.chop_char()
                type_ = TokenType.NEQ
                return Token(literal, type_, location)
            print(f"{location}:ERROR: `!{self.chop_char()}` is not a valid symbol")
        elif self.program_string[self.cursor] == '=':
            if self.cursor + 1 < len(self.program_string) and self.program_string[self.cursor + 1] == '=':
                literal = self.chop_char() + self.chop_char()
                type_ = TokenType.EQ
            else :
                literal = self.chop_char()
                type_ = TokenType.ASSIGN
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == '-':
            literal = self.chop_char()
            type_ = TokenType.MINUS
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == '+':
            literal = self.chop_char()
            type_ = TokenType.ADD
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == ';':
            literal = self.chop_char()
            type_ = TokenType.SEMICOLON
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == '(':
            literal = self.chop_char()
            type_ = TokenType.OPEN_PAREN
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == ')':
            literal = self.chop_char()
            type_ = TokenType.CLOSE_PAREN
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == '*':
            literal = self.chop_char()
            type_ = TokenType.MULT
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == '{':
            literal = self.chop_char()
            type_ = TokenType.OPEN_CURLY_BRACKET
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == '}':
            literal = self.chop_char()
            type_ = TokenType.CLOSE_CURLY_BRACKET
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == '[':
            literal = self.chop_char()
            type_ = TokenType.OPEN_BRACKET
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == ']':
            literal = self.chop_char()
            type_ = TokenType.CLOSE_BRACKET
            return Token(literal, type_, location)
        elif self.program_string[self.cursor] == ',':
            literal = self.chop_char()
            type_ = TokenType.COMMA
            return Token(literal, type_, location)
        else:
            print(self.program_string[self.cursor])
            todo()


class AST():
    def __init__(self, token: Token):
        self.token = token

    def to_dict(self):
       pass

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self):
        return self.__str__()

    def generate(self, generator, out_file):
        assert TokenType.TokenType_NUMBERS == 21




class BinaryOperator(AST):
    def __init__(self, token: Token, left: AST, right: AST):
        super().__init__(token)
        self.left = left
        self.right = right

    def to_dict(self):
        if self.left is None:
            ltd = None
        else:
            ltd = self.left.to_dict()
        if self.right is None:
            rtd = None
        else:
            rtd = self.right.to_dict()
        return dict(
            operator=self.token.literal,
            left=ltd,
            right=rtd,
        )

    def generate(self, generator, out_file):
        assert TokenType.TokenType_NUMBERS == 22
        if self.token.type == TokenType.MINUS:
            self.left.generate(generator, out_file)
            print(f"push rax", file=out_file)
            self.right.generate(generator, out_file)
            print(f"pop rbx", file=out_file)
            print(f"; MINUS", file=out_file)
            print(f"sub rbx, rax", file=out_file)
            print(f"mov rax, rbx", file=out_file)
        if self.token.type == TokenType.ADD:
            self.left.generate(generator, out_file)
            print(f"push rax", file=out_file)
            self.right.generate(generator, out_file)
            print(f"pop rbx", file=out_file)
            print(f"; ADD", file=out_file)
            print(f"add rax, rbx", file=out_file)
        elif self.token.type == TokenType.NEQ:
            self.left.generate(generator, out_file)
            print(f"push rax", file=out_file)
            self.right.generate(generator, out_file)
            print(f"pop rbx", file=out_file)
            print(f"; NEQ", file=out_file)
            print(f"cmp rax, rbx", file=out_file)
            print(f"setne al", file=out_file)
            print(f"movzx rax, al", file=out_file)
        elif self.token.type == TokenType.EQ:
            self.left.generate(generator, out_file)
            print(f"push rax", file=out_file)
            self.right.generate(generator, out_file)
            print(f"pop rbx", file=out_file)
            print(f"; EQ", file=out_file)
            print(f"cmp rax, rbx", file=out_file)
            print(f"sete al", file=out_file)
            print(f"movzx rax, al", file=out_file)
        elif self.token.type == TokenType.MULT:
            self.left.generate(generator, out_file)
            print(f"push rax", file=out_file)
            self.right.generate(generator, out_file)
            print(f"pop rbx", file=out_file)
            print(f"; MULT", file=out_file)
            print(f"mul rbx", file=out_file)



class IfNode(AST):
    def __init__(self, token: Token, condition: AST, body: AST):
        super().__init__(token)
        self.condition = condition
        self.body = body

    def to_dict(self):
        return dict(condition=self.condition.to_dict(), body=self.body.to_dict())

    def generate(self, generator, out_file):
        condition_label = generator.label_count
        generator.label_count += 1
        end_label = generator.label_count
        generator.label_count += 1
        print(f"; IF", file=out_file)
        print(f".L{condition_label}:", file=out_file)
        self.condition.generate(generator, out_file)
        print(f"cmp rax, 0", file=out_file)
        print(f"je .L{end_label}", file=out_file)
        self.body.generate(generator, out_file)
        print(f".L{end_label}:", file=out_file)


class WhileNode(AST):
    def __init__(self, token: Token, condition: AST, body: AST):
        super().__init__(token)
        self.condition = condition
        self.body = body
    def to_dict(self):
        return dict(condition=self.condition.to_dict(), body=self.body.to_dict())

    def generate(self, generator, out_file):
        condition_label = generator.label_count
        generator.label_count += 1
        end_label = generator.label_count
        generator.label_count += 1
        print(f"; WHILE", file=out_file)
        print(f".L{condition_label}:", file=out_file)
        self.condition.generate(generator, out_file)
        print(f"cmp rax, 0", file=out_file)
        print(f"je .L{end_label}", file=out_file)
        self.body.generate(generator, out_file)
        print(f"jmp .L{condition_label}", file=out_file)
        print(f".L{end_label}:", file=out_file)


class FunctionNode(AST):
    def __init__(self, token: Token, arguments: List[Token],
                 body: AST, name: Token):
        super().__init__(token)
        self.name = name
        self.arguments = arguments
        self.body = body
    def to_dict(self):
        return dict(name=self.name.literal,
                    arguments=[a.to_dict() for a in self.arguments], body=self.body.to_dict())

    def generate(self, generator, out_file):
        function_name = self.name.literal
        if function_name in generator.functions:
            print(f"{self.token.location}: ERROR: function name already exists")
        if function_name in generator.variables:
            print(f"{self.token.location}: ERROR: this token already exists. This is a variable.")
        asm_func_name = f"FUNC_{function_name}"
        if function_name == 'main':
            asm_func_name = "start"
        generator.functions[function_name] = asm_func_name

        new_gen = generator

        if function_name != 'main':
            new_gen = Generator(generator.statements)
            new_gen.memory_depth = generator.memory_depth
            new_gen.functions = generator.functions
            new_gen.label_count = generator.label_count

        print(f"{asm_func_name}:", file=out_file)

        function_stack = 0
        for arg in self.arguments:
            identifier = arg.literal

            new_gen.variables[identifier] =f"[mem+{new_gen.memory_depth}]"
            print(f"mov r10, qword [fstack+{function_stack}]", file=out_file)
            print(f"mov qword {new_gen.variables[identifier]}, r10", file=out_file)

            new_gen.memory_depth += 8
            function_stack += 8

        self.body.generate(new_gen, out_file)
        if function_name != 'main':
            print(f"ret", file=out_file)
        generator.label_count = new_gen.label_count
        generator.memory_depth = new_gen.memory_depth # TODO optimize memory


class FunctionCall(AST):
    def __init__(self, token: Token, arguments: List[AST]):
        super().__init__(token)
        self.arguments = arguments

    def to_dict(self):
        return dict(arguments=[a.to_dict() for a in self.arguments])

    def generate(self, generator, out_file):
        identifier = self.token.literal
        function_stack = 0
        if identifier not in generator.functions:
            print(f"{self.token.location}: ERROR: no function named `{identifier}`")
            exit(1)
        for arg in self.arguments:
            arg.generate(generator, out_file)
            print(f"mov qword [fstack+{function_stack}], rax", file=out_file)
            function_stack += 8  # TODO 8 = sizeof int
        print(f"call {generator.functions[identifier]}", file=out_file)


class BlockNode(AST):
    def __init__(self, token: Token, statements: List[AST]):
        super().__init__(token)
        self.statements: List[AST] = statements

    def to_dict(self):
        return dict(statements=[s.to_dict() for s in self.statements])

    def generate(self, generator, out_file):
        for statement in self.statements:
            statement.generate(generator, out_file)


class AssignNode(AST):
    def __init__(self, token: Token, variable: AST, expression: AST):
        super().__init__(token)
        self.variable = variable
        self.expression = expression

    def to_dict(self):
        return dict(variable=self.variable.to_dict(), expression=self.expression.to_dict())

    def generate(self, generator, out_file):
        identifier = self.variable.token.literal
        self.expression.generate(generator, out_file)
        if identifier in generator.functions:
            print(f"{self.token.location}: ERROR: cannot assign to a function.")
            exit(1)
        if identifier not in generator.variables:
            print(f"{self.token.location}: ERROR: unknown word `{identifier}`.")
            exit(1)
        if generator.variables[identifier] is None:
            generator.variables[identifier] = f"[mem+{generator.memory_depth}]"
            generator.memory_depth += 8
        print(f"; ASSIGN", file=out_file)
        if isinstance(self.variable, TableAccessNode):
            print("push rax", file=out_file)
            self.variable.generate(generator, out_file)
            print("pop rax ", file=out_file)
            print("mov qword [rbx], rax", file=out_file)
        else:
            print(f"mov qword {generator.variables[identifier]}, rax", file=out_file)


class PutcNode(AST):
    def __init__(self, token: Token, expression: AST):
        super().__init__(token)
        self.expression = expression

    def to_dict(self):
        return dict(expression=self.expression.to_dict())

    def generate(self, generator, out_file):
        self.expression.generate(generator, out_file)
        print(f"; PUTC", file=out_file)
        mem_addr = f"[mem+{generator.memory_depth}]"
        generator.memory_depth += 8 # TODO optimize memory
        print(f"mov qword {mem_addr}, rax", file=out_file)
        print(f"lea rsi, {mem_addr}", file=out_file)
        print("mov rdx, 8", file=out_file)
        print("mov rdi, 1", file=out_file)
        print("mov rax, 1", file=out_file)
        print("syscall", file=out_file)


class VariableDeclarationNode(AST):
    def __init__(self, token: Token, variable: Token):
        super().__init__(token)
        self.variable = variable

    def to_dict(self):
        return dict(variable=self.variable.to_dict())
    def generate(self, generator, out_file):
        generator.variables[self.variable.literal] = None


class IntNode(AST):
    def __init__(self, token: Token):
        super().__init__(token)
        self.value = token.literal

    def to_dict(self):
        return dict(value=self.value)

    def generate(self, generator, out_file):
        print(f"; INT", file=out_file)
        print(f"mov rax, {self.token.literal}", file=out_file)



class IdentifierNode(AST):
    def __init__(self, token: Token):
        super().__init__(token)
        self.value = token.literal

    def to_dict(self):
        return dict(value=self.value)

    def generate(self, generator, out_file):
        identifier = self.token.literal
        if identifier not in generator.variables and identifier not in generator.functions:
            print(f"{self.token.location}: ERROR: identifier `{identifier}` is not declared")
            exit(1)
        if generator.variables[identifier] is None:
            print(f"{self.token.location}: ERROR: identifier `{identifier}` is not assigned")
            exit(1)
        print(f"mov rax, qword {generator.variables[identifier]}", file=out_file)


class TableAccessNode(AST):
    def __init__(self, token: Token, index: AST):
        super().__init__(token)
        self.value = token.literal
        self.index = index

    def to_dict(self):
        return dict(value=self.value, index=self.index.to_dict())

    def generate(self, generator, out_file):
        identifier = self.token.literal
        if identifier not in generator.variables and identifier not in generator.functions:
            print(f"{self.token.location}: ERROR: identifier `{identifier}` is not declared")
            exit(1)
        if generator.variables[identifier] is None:
            print(f"{self.token.location}: ERROR: identifier `{identifier}` is not assigned")
            exit(1)
        self.index.generate(generator, out_file)
        if generator.variables[identifier].startswith("[mem+"):
            var_index = generator.variables[identifier][len("[mem+"):-len("]")]
            mem = "mem+"
            var = mem + var_index
        elif generator.variables[identifier].startswith("[fstack+"):
            print("COMPILER ERROR, FSTACK IS BEING USED ")
        else:
            print("COMPILER ERROR, UNREACHABLE")
            exit(1)
        sizeof_var = 8  # TODO  sizeof VAR at compile time (when adding struct ?)
        # rax is the index
        print(f"mov r10, qword [{var}]", file=out_file)
        print(f"mov rcx, {sizeof_var}",file=out_file)
        print("mul rcx", file=out_file)
        print("add rax, r10", file=out_file)
        print(f"mov rbx, rax",file=out_file)
        print(f"mov rax, qword [rbx]", file=out_file)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.cursor = 0

    def parse(self):
        return self.statement_list()

    def statement_list(self):
        result = list()
        while self.cursor < len(self.tokens) and self.current_token() != TokenType.CLOSE_CURLY_BRACKET:
            result.append(self.parse_statement())
        return result

    def parse_statement(self):
        if debug:
            print(self.current_token_location())
        if self.current_token() == TokenType.IF:
            return self.parse_if()
        if self.current_token() == TokenType.WHILE:
            return self.parse_while()
        if self.current_token() == TokenType.OPEN_CURLY_BRACKET:
            return self.parse_block()
        if self.current_token() == TokenType.IDENTIFIER:
            if self.tokens[self.cursor+1].type == TokenType.OPEN_BRACKET:
                return self.parse_table_access_for_assigment()
            if self.tokens[self.cursor+1].type == TokenType.ASSIGN:
                return self.parse_assign()
            if self.tokens[self.cursor+1].type == TokenType.OPEN_PAREN:
                return self.parse_function_call()
        if self.current_token() == TokenType.FUNCTION:
            return self.parse_function()
        if self.current_token() == TokenType.PUTC:
            return self.parse_putc()
        if self.current_token() == TokenType.LET:
            return self.parse_var_declaration()


    def parse_expr(self) -> AST:
        assert TokenType.TokenType_NUMBERS == 22
        left = self.parse_T()
        if self.current_token() == TokenType.MINUS:
            token = self.chop_token()
            right = self.parse_expr()
            return BinaryOperator(token, left, right)
        if self.current_token() == TokenType.ADD:
            token = self.chop_token()
            right = self.parse_expr()
            return BinaryOperator(token, left, right)
        elif self.current_token() == TokenType.EQ:
            token = self.chop_token()
            right = self.parse_expr()
            return BinaryOperator(token, left, right)
        elif self.current_token() == TokenType.NEQ:
            token = self.chop_token()
            right = self.parse_expr()
            return BinaryOperator(token, left, right)
        else:
            return left

    def parse_T(self) -> AST:
        left = self.parse_Q()
        if self.current_token() == TokenType.MULT:
            token = self.chop_token()
            right = self.parse_T()
            return BinaryOperator(token, left, right)
        else:
            return left

    def parse_Q(self) -> AST:
        if self.current_token() == TokenType.OPEN_PAREN:
            self.chop_token()
            expr = self.parse_expr()
            if self.chop_token().type != TokenType.CLOSE_PAREN:
                raise ValueError
            return expr
        elif self.current_token() == TokenType.STRING:
            chopped_token = self.chop_token()
            node = ArrayNode(chopped_token, list())
            for c in chopped_token.literal:
                node.add(Token(str(ord(c)), TokenType.STRING, chopped_token.location)) # TODO location here
            node.add(Token("0", TokenType.INT, chopped_token.location))  # cString TODO location here
            return node
        elif self.current_token() == TokenType.INT:
            return IntNode(self.chop_token())
        elif self.current_token() == TokenType.IDENTIFIER:
            if self.cursor + 1 < len(self.tokens) and self.tokens[self.cursor + 1].type == TokenType.OPEN_BRACKET:
                token = self.chop_token()
                self.chop_token()  # token [
                index = self.parse_expr()
                self.chop_token()  # token unction call]
                return TableAccessNode(token, index)
            else:
                return IdentifierNode(self.chop_token())
        elif self.current_token() == TokenType.OPEN_BRACKET:
            chopped_token = self.chop_token()   #  [
            node = ArrayNode(chopped_token, list())
            close_bracket = self.current_token() == TokenType.CLOSE_BRACKET
            while not close_bracket:
                node.add(self.chop_token())
                match self.current_token():
                    case TokenType.COMMA:
                        self.chop_token()
                    case TokenType.CLOSE_BRACKET:
                        close_bracket = True
                    case _:
                        comma = self.chop_token();
                        print(f"{comma.location}: ERROR: expected `,` after value in array, but got {comma.literal}")
                        exit(1)
            self.chop_token()
            return node
        print(f"{self.current_token_location()}: ERROR: Non existing expression or unfinished statement")
        exit(1)

    def parse_if(self):
        token = self.chop_token()
        if self.chop_token().type != TokenType.OPEN_PAREN:
            print(f"{token.location}: ERROR: if is not followed by a parenthesis.")
            exit(1)
        condition = self.parse_expr()
        if self.chop_token().type != TokenType.CLOSE_PAREN:
            print(f"{token.location}: ERROR: the parenthesis is not closed.")
            exit(1)
        body = self.parse_statement()
        return IfNode(token, condition, body)

    def parse_while(self):
        token = self.chop_token()
        if self.chop_token().type != TokenType.OPEN_PAREN:
            print(f"{token.location}: ERROR: while is not followed by a parenthesis.")
            exit(1)
        condition = self.parse_expr()
        if self.chop_token().type != TokenType.CLOSE_PAREN:
            print(f"{token.location}: ERROR: the parenthesis is not closed.")
            exit(1)
        body = self.parse_statement()
        return WhileNode(token, condition, body)

    def parse_function(self):
        token = self.chop_token()
        function_name_token = self.chop_token()
        function_name = function_name_token.literal

        if self.chop_token().type != TokenType.OPEN_PAREN:
            print(f"{token.location}: ERROR: the function name `{function_name}` is not followed by a parenthesis.")
            exit(1)

        args = list()
        close_paren = self.current_token() == TokenType.CLOSE_PAREN
        while not close_paren:
            arg = self.chop_token()
            args.append(arg)
            if len(self.tokens) <= self.cursor:
                print(f"{token.location}: ERROR: the parenthesis is not closed.")
                exit(1)

            if arg.type != TokenType.IDENTIFIER:
                print(f"{token.location}: ERROR: the arg is `{arg.literal}`, this is not an identifier.")
                exit(1)
            match self.current_token():
                case TokenType.COMMA:
                   self.chop_token()
                case TokenType.CLOSE_PAREN:
                    close_paren = True
                case _:
                    print(f"{token.location}: ERROR: no comma after identifier.")
                    exit(1)
        self.chop_token()
        body = self.parse_statement()
        return FunctionNode(token, args, body, function_name_token)

    def current_token(self):
        if self.cursor > len(self.tokens):
            raise Exception
        return self.tokens[self.cursor].type

    def current_token_location(self) -> Location:
        if self.cursor > len(self.tokens):
            raise Exception
        return self.tokens[self.cursor].location

    def chop_token(self) -> Token:
        if self.cursor >= len(self.tokens):
            raise ValueError
        cursor = self.cursor
        self.cursor += 1
        return self.tokens[cursor]

    def parse_block(self) -> AST:
        token = self.chop_token()
        if token.type != TokenType.OPEN_CURLY_BRACKET:
            print(f"{token.location}: ERROR: if is not followed by a curly bracket.")
            exit(1)
        body = self.parse()
        if self.chop_token().type != TokenType.CLOSE_CURLY_BRACKET:
            print(f"{token.location}: ERROR: the curly bracket is not closed.")
            exit(1)
        return BlockNode(token, body)

    def parse_assign(self) -> AST:
        variable_token = self.chop_token()
        variable = IdentifierNode(variable_token)
        token = self.chop_token()
        expression = self.parse_expr()
        ct = self.chop_token()
        if ct.type != TokenType.SEMICOLON:
           print(f"{ct.location}:ERROR: missing `;`")
           exit(1)
        return AssignNode(token, variable, expression)

    def parse_putc(self) -> AST:
       token = self.chop_token()
       expression = self.parse_expr()
       ct = self.chop_token()
       if ct.type != TokenType.SEMICOLON:
           print(f"{ct.location}:ERROR: missing `;`")
           exit(1)
       return PutcNode(token, expression)

    def parse_function_call(self) -> AST:
        token = self.chop_token()
        self.chop_token()  # token (
        fun_call = FunctionCall(token, list())
        close_paren = self.current_token() == TokenType.CLOSE_PAREN
        while not close_paren: # ( 1, 3, 4, 5);
            fun_call.arguments.append(self.parse_expr())
            match self.current_token():
                case TokenType.COMMA:
                    self.chop_token()
                case TokenType.CLOSE_PAREN:
                    close_paren = True
                case _:
                    print(f"{self.chop_token().location}: ERROR: no comma after value in function call")
                    exit(1)
        self.chop_token() # I don't know why, and i don't want to think about it
        ct = self.chop_token()
        if ct.type != TokenType.SEMICOLON:
            print(f"{ct.location}: ERROR: missing semicolon")
        return fun_call

    def parse_var_declaration(self) -> AST:
        token = self.chop_token()
        variable = self.chop_token()
        semicolon = self.chop_token()
        if semicolon.type != TokenType.SEMICOLON:
            print(f"{semicolon.location}: ERROR: missing semicolon")
        return VariableDeclarationNode(token, variable)

    def parse_table_access_for_assigment(self) -> AST:
        identifier = self.chop_token()
        self.chop_token() # [
        index = self.parse_expr()
        self.chop_token() # ]
        tan = TableAccessNode(identifier, index)
        optoken = self.chop_token()
        if optoken.type == TokenType.ASSIGN:
            expression = self.parse_expr()
            ct = self.chop_token()
            if ct.type != TokenType.SEMICOLON:
                print(f"{ct.location}:ERROR: missing `;`")
                exit(1)
            return AssignNode(optoken, tan, expression)





class Generator:
    def __init__(self, statements: List[AST], out_file_name="foo.asm"):
        self.out_file = None
        self.statements = statements
        self.variables: Dict[str, str] = dict()
        self.functions: Dict[str, str] = dict()
        self.out_file_name = out_file_name
        self.memory_depth = 0
        self.label_count = 0

    def generate(self):
        out_file = open(self.out_file_name, "w")
        # Allocate static memory to do operations

        print("format ELF64 executable", file=out_file)
        print("segment readable executable", file=out_file)
        print("    entry start", file=out_file)
        for i, statement in enumerate(self.statements):
            if i != 0:
                print(f".l{i}:", file=out_file)
            statement.generate(self, out_file)

        print("; STOP", file=out_file)
        print("mov rax, 60", file=out_file)
        print("xor rdi, rdi", file=out_file)
        print("syscall", file=out_file)

        print("segment readable writable", file=out_file)

        for n, string in enumerate(strings):
            print(f"string_{n} dq ", end="", file=out_file)
            for i, token in enumerate(string):
                char = token.literal
                if i !=  0:
                    print(",", end="", file=out_file)
                print(f"{char}", end="", file=out_file)
            print(f"", file=out_file)
        print(f"fstack rb {8 << MAX_ARGS}", file=out_file)
        print(f"mem rb {STATIC_MEMORY_SIZE}", file=out_file)
        out_file.close()

    def deepcopy(self):
        statements = copy.deepcopy(self.statements)
        out_file_name = copy.deepcopy(self.out_file_name)

        gen = Generator(statements, out_file_name)
        gen.functions = copy.deepcopy(self.functions)
        gen.memory_depth = copy.deepcopy(self.memory_depth)
        gen.label_count = copy.deepcopy(self.label_count)

        return gen



class ArrayNode(AST):
    def __init__(self, token: Token, array: List[Token]):
        super().__init__(token)
        self.array = array
        self.size = 0
    def add(self, item):
        self.array.append(item)
        self.size += 1
    def generate(self, generator, out_file):
        global strings
        global string_length
        first_raw = generator.memory_depth
        print(f"; ARRAYNODE", file=out_file)
        if self.token.type == TokenType.STRING:
            strings.append([ord_ for ord_ in self.array])
            print(f"lea rax, [string_{string_length}]", file=out_file)
            string_length += 1
        else:
            for i in range(len(self.array)):
                print(f"mov qword [mem+{generator.memory_depth}], {self.array[i].literal}",
                      file=out_file)
                generator.memory_depth += 8
            print(f"lea rax, qword [mem+{first_raw}]", file=out_file)


def run_info(command: List[str]) -> None:
    if info_cmd:
        print(f"[INFO] {' '.join(command)}")
    subprocess.run(command)


def print_info(string: str):
    if info:
        print(f"[INFO] {string}")


def main() -> None:
    args = sys.argv
    (program_name, args) = shift_args(args)
    if len(args) != 2:
        print("ERROR: ", file=sys.stderr)
        usage(program_name)
        exit(1)
    (input_file, args) = shift_args(args)
    (output_file, args) = shift_args(args)

    input_file = os.path.abspath(input_file)

    f = open(input_file, "r")
    program_string = f.read()
    f.close()

    lexer = Lexer(input_file, program_string)

    begin = time.time()
    tokens = list()
    for token in lexer:
        tokens.append(token)
    end = time.time()
    print_info(f"tokenizing took {end-begin} seconds")

    begin = time.time()
    parser = Parser(tokens)
    statements = parser.parse()
    end = time.time()
    print_info(f"parsing took {end-begin} seconds")

    #  print(statements)

    begin = time.time()
    asm_file = output_file + ".asm"
    generator = Generator(statements, asm_file)
    generator.generate()
    end = time.time()
    print_info(f"generation took {end-begin} seconds")


    fasm_run = subprocess.run([fasm_loc, asm_file])
    if fasm_run.returncode > 0:
        exit(1)
    run_info(["chmod", "+x", output_file])


if __name__ == '__main__':
    main()
