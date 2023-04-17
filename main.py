#!/usr/bin/env python3.11
import json
import os.path
import subprocess
from typing import List, Optional
import sys

STATIC_MEMORY_SIZE = 1024 * 1024 * 8


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
    PUTC = auto()
    NEQ = auto()
    WHILE = auto()
    STRING = auto()
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
        assert TokenType.TokenType_NUMBERS == 17
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
                print(literal)
            self.chop_char()
            type_ = TokenType.STRING
            return Token(literal, type_, location)
        elif self.program_string[self.cursor].isalpha():
            while self.program_string[self.cursor].isalnum():
                self.chop_char()
            literal = self.program_string[cursor:self.cursor]
            type_ = TokenType.IDENTIFIER
            if literal == 'putc':
                type_ = TokenType.PUTC
            elif literal == 'while':
                type_ = TokenType.WHILE
            return Token(literal, type_, location)
        elif self.program_string[self.cursor].isnumeric():
            while self.program_string[self.cursor].isalnum():
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

    def generate(self, generator):
        assert TokenType.TokenType_NUMBERS == 17
        if isinstance(self.token, ArrayNode):
            first_raw = generator.memory_depth
            print(f"; ARRAYNODE", file=generator.out_file)
            for i in range(len(self.token.array)):
                print(f"mov qword [global_mem+{generator.memory_depth}], {self.token.array[i].literal}",
                      file=generator.out_file)
                generator.memory_depth += 8
            print(f"lea rax, [global_mem+{first_raw}]", file=generator.out_file)
        elif self.token.type == TokenType.ASSIGN:
            self.right.generate(generator)
            identifier = self.left.token.literal
            if identifier not in generator.variables:
                generator.variables[identifier] = f"[global_mem+{generator.memory_depth}]"
                generator.memory_depth += 8
            print(f"; ASSIGN", file=generator.out_file)
            print(f"mov {generator.variables[identifier]}, rax", file=generator.out_file)
        elif self.token.type == TokenType.ADD:
            self.left.generate(generator)
            print(f"push rax", file=generator.out_file)
            self.right.generate(generator)
            print(f"pop rbx", file=generator.out_file)
            print(f"; ADD", file=generator.out_file)
            print(f"add rax, rbx", file=generator.out_file)
        elif self.token.type == TokenType.NEQ:
            self.left.generate(generator)
            print(f"push rax", file=generator.out_file)
            self.right.generate(generator)
            print(f"pop rbx", file=generator.out_file)
            print(f"; NEQ", file=generator.out_file)
            print(f"cmp rax, rbx", file=generator.out_file)
            print(f"setne al", file=generator.out_file)
            print(f"movzx rax, al", file=generator.out_file)
        elif self.token.type == TokenType.MULT:
            self.left.generate(generator)
            print(f"push rax", file=generator.out_file)
            self.right.generate(generator)
            print(f"pop rbx", file=generator.out_file)
            print(f"; MULT", file=generator.out_file)
            print(f"mul rbx", file=generator.out_file)
        elif self.token.type == TokenType.IDENTIFIER:
            identifier = self.token.literal
            if identifier not in generator.variables:
                print(f"ERROR:{self.token.location}: identifier `{identifier}` is not declared", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"; IDENTIFIER", file=generator.out_file)
                if self.right is not None:
                    self.right.generate(generator)
                    add_to_global_mem = generator.variables[identifier][len("[global_mem+"):-len("]")]
                    print(f"mov rbx, [global_mem+{add_to_global_mem}]", file=generator.out_file)
                    print(f"mov rax, [rbx+rax]", file=generator.out_file)
                else:
                    print(f"mov rax, {generator.variables[identifier]}", file=generator.out_file)
        elif self.token.type == TokenType.INT:
            print(f"; INT", file=generator.out_file)
            print(f"mov rax, {self.token.literal}", file=generator.out_file)
        elif self.token.type == TokenType.PUTC:
            self.right.generate(generator)
            print(f"; PUTC", file=generator.out_file)
            global_mem_addr = f"[global_mem+{generator.memory_depth}]"
            print(f"mov {global_mem_addr}, rax", file=generator.out_file)
            print(f"lea rsi, {global_mem_addr}", file=generator.out_file)
            print("mov rdx, 8", file=generator.out_file)
            print("mov rdi, 1", file=generator.out_file)
            print("mov rax, 1", file=generator.out_file)
            print("syscall", file=generator.out_file)
        elif self.token.type == TokenType.WHILE:
            assert isinstance(self, WhileNode)  # always true
            condition_label = generator.label_count
            generator.label_count += 1
            end_label = generator.label_count
            generator.label_count += 1
            print(f"; WHILE", file=generator.out_file)
            print(f".L{condition_label}:", file=generator.out_file)
            self.condition.generate(generator)
            print(f"cmp rax, 0", file=generator.out_file)
            print(f"je .L{end_label}", file=generator.out_file)
            for ast in self.body:
                ast.generate(generator)
            print(f"jmp .L{condition_label}", file=generator.out_file)
            print(f".L{end_label}:", file=generator.out_file)


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
        assert TokenType.TokenType_NUMBERS == 17
        left = self.parse_T()
        if self.current_token() == TokenType.ADD:
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
        if left is None:
            return
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
            token = ArrayNode("..", self.current_token(), chopped_token.location)
            for c in chopped_token.literal:
                token.array.append(Token(str(ord(c)), TokenType.INT, chopped_token.location)) # TODO location here
            token.array.append(Token("0", TokenType.INT, chopped_token.location))  # cString TODO location here
            return AST(token, None, None)
        elif self.current_token() == TokenType.INT:
            return AST(self.chop_token(), None, None)
        elif self.current_token() == TokenType.IDENTIFIER:
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
                token.array.append(value_token)
                comma = self.chop_token()
                if comma.type != TokenType.COMMA:
                    print(f"ERROR:{comma.location}: no comma after value in array")
                    exit(1)
            self.chop_token()
            return AST(token, None, None)
        elif self.current_token() == TokenType.WHILE:
            return self.parse_while()
        elif self.current_token() == TokenType.PUTC:
            token = self.chop_token()
            right = self.parse_S()
            return AST(token, None, right)
        elif self.current_token() == TokenType.SEMICOLON:
            self.chop_token()

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

    def current_token(self):
        if self.cursor >= len(self.tokens):
            raise Exception;
        return self.tokens[self.cursor].type

    def chop_token(self):
        if self.cursor >= len(self.tokens):
            raise ValueError
        cursor = self.cursor
        self.cursor += 1
        return self.tokens[cursor]


class WhileNode(AST):
    def __init__(self, token: Token, left: AST | None, right: AST | None, condition: AST, body: List[AST | None]):
        super().__init__(token, left, right)
        self.condition = condition
        self.body = body


class Generator:
    def __init__(self, statements: List[AST], out_file_name="foo.asm"):
        self.out_file = None
        self.statements = statements
        self.variables = dict()
        self.out_file_name = out_file_name
        self.memory_depth = 0
        self.label_count = 0

    def generate(self):
        self.out_file = open(self.out_file_name, "w")
        # Allocate static memory to do operations
        print("section .data", file=self.out_file)
        print("     global_mem:", file=self.out_file)
        print("         align 4096", file=self.out_file)
        print(f"         times {STATIC_MEMORY_SIZE} db 0", file=self.out_file)
        print("section .text", file=self.out_file)
        print("    global _start", file=self.out_file)
        print("_start:", file=self.out_file)
        for i in range(len(self.statements)):
            if i != 0:
                print(f".l{i}:", file=self.out_file)
            self.statements[i].generate(self)

        print("; STOP", file=self.out_file)
        print("mov rax, 60", file=self.out_file)
        print("xor rdi, rdi", file=self.out_file)
        print("syscall", file=self.out_file)
        self.out_file.close()


class ArrayNode(Token):
    def __init__(self, literal, type_, location):
        super().__init__(literal, type_, location)
        self.array = list()


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
    obj_file = output_file + ".o"
    generator = Generator(statements, asm_file)
    generator.generate()

    run_info(["yasm", "-f", "elf64", "-o", obj_file, asm_file])
    run_info(["ld", obj_file, "-o", output_file])


if __name__ == '__main__':
    main()
