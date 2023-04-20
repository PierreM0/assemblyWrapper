#!/usr/bin/env python3.11
import copy
import json
import os.path
import subprocess
from typing import List, Optional
import sys

STATIC_MEMORY_SIZE = 1024 * 1024 * 8
MAX_ARGS = 5

def shift_args(args: List) -> (str, List):
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
            self.chop_char()
            if self.cursor >= len(self.program_string):
                raise StopIteration
            if self.program_string[self.cursor] == '\n':
                self.line += 1
                self.cursor_on_line = 1

    def __next__(self):
        assert TokenType.TokenType_NUMBERS == 20
        if self.cursor >= len(self.program_string):
            raise StopIteration
        self.trim_left()

        cursor = self.cursor
        location = Location(self.line, self.cursor, self.input_file)
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
            print(f"ERROR:{location} `!{self.chop_char()}` is not a valid symbol")
        elif self.program_string[self.cursor] == '=':
            if self.cursor + 1 < len(self.program_string) and self.program_string[self.cursor + 1] == '=':
                literal = self.chop_char() + self.chop_char()
                type_ = TokenType.EQ
            else :
                literal = self.chop_char()
                type_ = TokenType.ASSIGN
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


class AST:
    def __init__(self, token: Token, left: Optional["AST"], right: Optional["AST"]):
        self.token = token
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
            token=self.token.to_dict(),
            left=ltd,
            right=rtd,
        )

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self):
        return self.__str__()

    def generate(self, generator, out_file):
        assert TokenType.TokenType_NUMBERS == 20
        if isinstance(self.token, ArrayNode):
            first_raw = generator.memory_depth
            print(f"; ARRAYNODE", file=out_file)
            if self.token.type == TokenType.STRING:
                generator.strings.append([ord_ for ord_ in self.token.array])
                print(f"lea rax, [string_{generator.string_len}]", file=out_file)
                generator.string_len += 1
            else:
                for i in range(len(self.token.array)):
                    print(f"mov qword [mem+{generator.memory_depth}], {self.token.array[i].literal}",
                          file=out_file)
                    generator.memory_depth += 8
                print(f"lea rax, qword [mem+{first_raw}]", file=out_file)
        elif self.token.type == TokenType.ASSIGN:
            self.right.generate(generator, out_file)
            identifier = self.left.token.literal
            if identifier in generator.functions:
                print(f"ERROR: {self.token.location}: cannot assign to a function.")
            if identifier not in generator.variables:
                generator.variables[identifier] = f"[mem+{generator.memory_depth}]"
                generator.memory_depth += 8
            print(f"; ASSIGN", file=out_file)
            print(f"mov qword {generator.variables[identifier]}, rax", file=out_file)
        elif self.token.type == TokenType.ADD:
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
        elif self.token.type == TokenType.IDENTIFIER:
            identifier = self.token.literal
            if identifier not in generator.variables and identifier not in generator.functions:
                print(f"ERROR:{self.token.location}: identifier `{identifier}` is not declared", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"; IDENTIFIER", file=out_file)
                if isinstance(self, FunctionCall):
                    function_stack = 0
                    for arg in self.arguments:
                        arg.generate(generator, out_file)
                        print(f"mov qword [fstack+{function_stack}], rax", file=out_file)
                        function_stack += 8  # TODO 8 = sizeof int
                    print(f"call {generator.functions[identifier]}", file=out_file)
                elif self.right is not None:
                    self.right.generate(generator, out_file)
                    if generator.variables[identifier].startswith("[mem+"):
                        add_to_mem = generator.variables[identifier][len("[mem+"):-len("]")]
                        mem="mem"
                    if generator.variables[identifier].startswith("[fstack+"):
                        add_to_mem = generator.variables[identifier][len("[fstack+"):-len("]")]
                        mem="fstack"
                    sizeof_var = 8  # TODO  sizeof VAR at compile time (when adding struct ?)
                    print(f"mov rbx, {sizeof_var}", file=out_file)
                    print(f"mul rbx", file=out_file)
                    print(f"mov rbx, qword [{mem}+{add_to_mem}*{sizeof_var}]", file=out_file)
                    print(f"mov rax, qword [rbx+rax]", file=out_file)
                else:
                    print(f"mov rax, qword {generator.variables[identifier]}", file=out_file)
        elif self.token.type == TokenType.INT:
            print(f"; INT", file=out_file)
            print(f"mov rax, {self.token.literal}", file=out_file)
        elif self.token.type == TokenType.PUTC:
            self.right.generate(generator, out_file)
            print(f"; PUTC", file=out_file)
            mem_addr = f"[mem+{generator.memory_depth}]"
            print(f"mov qword {mem_addr}, rax", file=out_file)
            print(f"lea rsi, {mem_addr}", file=out_file)
            print("mov rdx, 8", file=out_file)
            print("mov rdi, 1", file=out_file)
            print("mov rax, 1", file=out_file)
            print("syscall", file=out_file)
        elif self.token.type == TokenType.WHILE:
            assert isinstance(self, WhileNode)  # always true
            condition_label = generator.label_count
            generator.label_count += 1
            end_label = generator.label_count
            generator.label_count += 1
            print(f"; WHILE", file=out_file)
            print(f".L{condition_label}:", file=out_file)
            self.condition.generate(generator, out_file)
            print(f"cmp rax, 0", file=out_file)
            print(f"je .L{end_label}", file=out_file)
            for ast in self.body:
                ast.generate(generator, out_file)
            print(f"jmp .L{condition_label}", file=out_file)
            print(f".L{end_label}:", file=out_file)
        elif self.token.type == TokenType.IF:
            assert isinstance(self, IfNode)  # always true
            condition_label = generator.label_count
            generator.label_count += 1
            end_label = generator.label_count
            generator.label_count += 1
            print(f"; IF", file=out_file)
            print(f".L{condition_label}:", file=out_file)
            self.condition.generate(generator, out_file)
            print(f"cmp rax, 0", file=out_file)
            print(f"je .L{end_label}", file=out_file)
            for ast in self.body:
                ast.generate(generator, out_file)
            print(f".L{end_label}:", file=out_file)
        elif self.token.type == TokenType.FUNCTION:
            assert isinstance(self, FunctionNode)
            function_name = self.name.literal
            if function_name in generator.functions:
                print(f"ERROR:{self.token.location}: function name already exists")
            if function_name in generator.variables:
                print(f"ERROR:{self.token.location}: this token already exists. This is a variable.")
            asm_func_name = f"FUNC_{function_name}"
            if function_name == 'main':
                asm_func_name = "start"
            generator.functions[function_name] = asm_func_name

            if function_name != 'main':
                generator = generator.deepcopy()

            function_stack = 0
            for arg in self.arguments:
                identifier = arg.literal

                generator.variables[identifier] = f"[fstack+{function_stack}]"
                function_stack += 8

            print(f"{asm_func_name}:", file=out_file)
            for statements in self.body:
                statements.generate(generator, out_file)
            if function_name != 'main':
                print(f"ret",file=out_file)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.cursor = 0

    def parse(self):
        result = list()
        a = 0
        while self.cursor < len(self.tokens) and self.current_token() != TokenType.CLOSE_CURLY_BRACKET:
            parsed_ast = self.parse_S()
            if self.current_token() == TokenType.SEMICOLON:
                self.chop_token()
            result.append(parsed_ast)
        return result

    def parse_S(self) -> AST | None:
        assert TokenType.TokenType_NUMBERS == 20
        left = self.parse_T()
        if self.current_token() == TokenType.ADD:
            token = self.chop_token()
            right = self.parse_S()
            return AST(token, left, right)
        elif self.current_token() == TokenType.EQ:
            token = self.chop_token()
            right = self.parse_S()
            return AST(token, left, right)
        elif self.current_token() == TokenType.NEQ:
            token = self.chop_token()
            right = self.parse_S()
            return AST(token, left, right)
        elif self.current_token() == TokenType.ASSIGN:
            token = self.chop_token()
            right = self.parse_S()
            return AST(token, left, right)
        else:
            return left

    def parse_T(self):
        left = self.parse_Q()
        if self.current_token() == TokenType.MULT:
            token = self.chop_token()
            right = self.parse_T()
            return AST(token, left, right)
        else:
            return left

    def parse_Q(self):
        if self.current_token() == TokenType.OPEN_PAREN:
            self.chop_token()
            expr = self.parse_S()
            if self.chop_token().type != TokenType.CLOSE_PAREN:
                raise ValueError
            return expr
        elif self.current_token() == TokenType.STRING:
            chopped_token = self.chop_token()
            token = ArrayNode("..", chopped_token.type, chopped_token.location)
            for c in chopped_token.literal:
                token.add(Token(str(ord(c)), TokenType.STRING, chopped_token.location)) # TODO location here
            token.add(Token("0", TokenType.INT, chopped_token.location))  # cString TODO location here
            return AST(token, None, None)
        elif self.current_token() == TokenType.INT:
            return AST(self.chop_token(), None, None)
        elif self.current_token() == TokenType.IDENTIFIER:
            if self.cursor + 1 < len(self.tokens) and self.tokens[self.cursor + 1].type == TokenType.OPEN_PAREN:
                token = self.chop_token()
                self.chop_token()  # token (
                fun_call = FunctionCall(token, None, None, list())
                while self.current_token() != TokenType.CLOSE_PAREN:
                    fun_call.arguments.append(self.parse_S())
                    match self.current_token():
                        case TokenType.COMMA:
                            self.chop_token()
                        case TokenType.CLOSE_PAREN:
                            pass
                        case _:
                            print(f"ERROR:{self.chop_token().location}: no comma after value in function call")
                            exit(1)
                self.chop_token()
                return fun_call

            if self.cursor + 1 < len(self.tokens) and self.tokens[self.cursor + 1].type == TokenType.OPEN_BRACKET:
                token = self.chop_token()
                self.chop_token()  # token [
                right = self.parse_S()
                self.chop_token()  # token ]
                return AST(token, None, right)
            else:
                return AST(self.chop_token(), None, None)
        elif self.current_token() == TokenType.OPEN_BRACKET:
            chopped_token = self.chop_token()
            token = ArrayNode("[..]", self.current_token(), chopped_token.location)
            if token.type != TokenType.INT:  # TODO update this
                raise ValueError
            while self.current_token() != TokenType.CLOSE_BRACKET:
                value_token = self.chop_token()
                if value_token.type != token.type:
                    raise ValueError
                token.add(value_token)
                comma = self.chop_token()
                match self.current_token():
                    case TokenType.COMMA | TokenType.CLOSE_PAREN:
                        arg = self.chop_token()
                    case _:
                        print(f"ERROR:{comma.location}: no comma after value in array")
                        exit(1)
            self.chop_token()
            return AST(token, None, None)
        elif self.current_token() == TokenType.IF:
            return self.parse_if()
        elif self.current_token() == TokenType.WHILE:
            return self.parse_while()
        elif self.current_token() == TokenType.FUNCTION:
            return self.parse_function()
        elif self.current_token() == TokenType.PUTC:
            token = self.chop_token()
            right = self.parse_S()
            return AST(token, None, right)
        elif self.current_token() == TokenType.SEMICOLON:
            pass

    def parse_if(self):
        token = self.chop_token()
        if self.chop_token().type != TokenType.OPEN_PAREN:
            print(f"ERROR:{token.location}: if is not followed by a parenthesis.")
            exit(1)
        condition = self.parse_S()
        if self.chop_token().type != TokenType.CLOSE_PAREN:
            print(f"ERROR:{token.location}: the parenthesis is not closed.")
            exit(1)
        if self.chop_token().type != TokenType.OPEN_CURLY_BRACKET:
            print(f"ERROR:{token.location}: if is not followed by a curly bracket.")
            exit(1)
        body = self.parse()
        if self.chop_token().type != TokenType.CLOSE_CURLY_BRACKET:
            print(f"ERROR:{token.location}: the curly bracket is not closed.")
            exit(1)
        return IfNode(token, None, None, condition, body)

    def parse_while(self):
        token = self.chop_token()
        if self.chop_token().type != TokenType.OPEN_PAREN:
            print(f"ERROR:{token.location}: while is not followed by a parenthesis.")
            exit(1)
        condition = self.parse_S()
        if self.chop_token().type != TokenType.CLOSE_PAREN:
            print(f"ERROR:{token.location}: the parenthesis is not closed.")
            exit(1)
        if self.chop_token().type != TokenType.OPEN_CURLY_BRACKET:
            print(f"ERROR:{token.location}: while is not followed by a curly bracket.")
            exit(1)
        body = self.parse()
        if self.chop_token().type != TokenType.CLOSE_CURLY_BRACKET:
            print(f"ERROR:{token.location}: the curly bracket is not closed.")
            exit(1)
        return WhileNode(token, None, None, condition, body)

    def parse_function(self):
        token = self.chop_token()
        function_name_token = self.chop_token()
        function_name = function_name_token.literal

        if self.chop_token().type != TokenType.OPEN_PAREN:
            print(f"ERROR:{token.location}: the function name `{function_name}` is not followed by a parenthesis.")
            exit(1)

        args = list()
        arg = self.chop_token()
        while arg.type != TokenType.CLOSE_PAREN:
            if len(self.tokens) <= self.cursor:
                print(f"ERROR:{token.location}: the parenthesis is not closed.")
                exit(1)

            if arg.type != TokenType.IDENTIFIER:
                print(f"ERROR:{token.location}: the parenthesis is not closed.")
                exit(1)

            args.append(arg)
            match self.current_token():
                case TokenType.COMMA | TokenType.CLOSE_PAREN:
                    arg = self.chop_token()
                case _:
                    print(f"ERROR:{token.location}: no comma after identifier.")
                    exit(1)

        if self.chop_token().type != TokenType.OPEN_CURLY_BRACKET:
            print(f"ERROR:{token.location}: `{function_name}` is not followed by a curly bracket.")
            exit(1)
        body = self.parse()
        if self.chop_token().type != TokenType.CLOSE_CURLY_BRACKET:
            print(f"ERROR:{token.location}: the curly bracket is not closed.")
            exit(1)
        return FunctionNode(token, None, None, args, body, function_name_token)

    def current_token(self):
        if self.cursor >= len(self.tokens):
            raise Exception
        return self.tokens[self.cursor].type

    def chop_token(self):
        if self.cursor >= len(self.tokens):
            raise ValueError
        cursor = self.cursor
        self.cursor += 1
        return self.tokens[cursor]


class IfNode(AST):
    def __init__(self, token: Token, left: AST | None, right: AST | None, condition: AST, body: List[AST | None]):
        super().__init__(token, left, right)
        self.condition = condition
        self.body = body

class WhileNode(AST):
    def __init__(self, token: Token, left: AST | None, right: AST | None, condition: AST, body: List[AST | None]):
        super().__init__(token, left, right)
        self.condition = condition
        self.body = body

class FunctionNode(AST):
    def __init__(self, token: Token, left: AST | None, right: AST | None, arguments: List[Token],
                 body: List[AST | None], name: Token):
        super().__init__(token, left, right)
        self.name = name
        self.arguments = arguments
        self.body = body

class FunctionCall(AST):
    def __init__(self, token: Token, left: AST | None, right: AST | None, arguments: List[AST]):
        super().__init__(token, left, right)
        self.arguments = arguments


class Generator:
    def __init__(self, statements: List[AST], out_file_name="foo.asm"):
        self.strings = list()
        self.string_len = 0
        self.out_file = None
        self.statements = statements
        self.variables = dict()
        self.functions = dict()
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

        for n, string in enumerate(self.strings):
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
        gen.strings = copy.deepcopy(self.strings)
        gen.string_len = copy.deepcopy(self.string_len)
        gen.variables = copy.deepcopy(self.variables)
        gen.functions = copy.deepcopy(self.functions)
        gen.memory_depth = copy.deepcopy(self.memory_depth)
        gen.label_count = copy.deepcopy(self.label_count)

        return gen



class ArrayNode(Token):
    def __init__(self, literal, type_, location):
        super().__init__(literal, type_, location)
        self.array = list()
        self.size = 0
    def add(self, item):
        self.array.append(item)
        self.size += 1


def run_info(command: List[str]) -> None:
    print(f"[INFO] {' '.join(command)}")
    subprocess.run(command)


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

    tokens = list()
    for token in lexer:
        tokens.append(token)

    parser = Parser(tokens)
    statements = parser.parse()

    asm_file = output_file + ".asm"
    generator = Generator(statements, asm_file)
    generator.generate()

    run_info(["fasm", asm_file])
    run_info(["chmod", "+x", output_file])


if __name__ == '__main__':
    main()
