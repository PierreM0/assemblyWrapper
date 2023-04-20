format ELF64 executable
segment readable executable
    entry start
FUNC_print:
; INT
mov rax, 0
; ASSIGN
mov qword [mem+0], rax
; WHILE
.L0:
; IDENTIFIER
; IDENTIFIER
mov rax, qword [mem+0]
mov rbx, 8
mul rbx
mov rbx, qword [fstack+0*8]
mov rax, qword [rbx+rax]
push rax
; INT
mov rax, 0
pop rbx
; NEQ
cmp rax, rbx
setne al
movzx rax, al
cmp rax, 0
je .L1
; IDENTIFIER
; IDENTIFIER
mov rax, qword [mem+0]
mov rbx, 8
mul rbx
mov rbx, qword [fstack+0*8]
mov rax, qword [rbx+rax]
; PUTC
mov qword [mem+8], rax
lea rsi, [mem+8]
mov rdx, 8
mov rdi, 1
mov rax, 1
syscall
; IDENTIFIER
mov rax, qword [mem+0]
push rax
; INT
mov rax, 1
pop rbx
; ADD
add rax, rbx
; ASSIGN
mov qword [mem+0], rax
jmp .L0
.L1:
ret
.l1:
FUNC_put_one_int:
; IDENTIFIER
mov rax, qword [fstack+0]
push rax
; INT
mov rax, 48
pop rbx
; ADD
add rax, rbx
; ASSIGN
mov qword [fstack+0], rax
; IDENTIFIER
mov rax, qword [fstack+0]
; PUTC
mov qword [mem+0], rax
lea rsi, [mem+0]
mov rdx, 8
mov rdi, 1
mov rax, 1
syscall
ret
.l2:
FUNC_println:
; IDENTIFIER
; IDENTIFIER
mov rax, qword [fstack+0]
mov qword [fstack+0], rax
call FUNC_print
; INT
mov rax, 10
; PUTC
mov qword [mem+0], rax
lea rsi, [mem+0]
mov rdx, 8
mov rdi, 1
mov rax, 1
syscall
ret
.l3:
start:
; ARRAYNODE
lea rax, [string_0]
; ASSIGN
mov qword [mem+0], rax
; IDENTIFIER
; IDENTIFIER
mov rax, qword [mem+0]
mov qword [fstack+0], rax
call FUNC_print
; IDENTIFIER
; INT
mov rax, 6
mov qword [fstack+0], rax
call FUNC_put_one_int
; IDENTIFIER
; INT
mov rax, 9
mov qword [fstack+0], rax
call FUNC_put_one_int
; INT
mov rax, 10
; PUTC
mov qword [mem+8], rax
lea rsi, [mem+8]
mov rdx, 8
mov rdi, 1
mov rax, 1
syscall
; ARRAYNODE
lea rax, [string_1]
; ASSIGN
mov qword [mem+0], rax
; IDENTIFIER
; IDENTIFIER
mov rax, qword [mem+0]
mov qword [fstack+0], rax
call FUNC_print
; ARRAYNODE
lea rax, [string_2]
; ASSIGN
mov qword [mem+0], rax
; IDENTIFIER
; IDENTIFIER
mov rax, qword [mem+0]
mov qword [fstack+0], rax
call FUNC_println
; STOP
mov rax, 60
xor rdi, rdi
syscall
segment readable writable
string_0 dq 72,101,108,108,111,44,32,87,111,114,108,100,10,0
string_1 dq 84,104,101,114,101,32,97,114,101,32,110,111,32,78,101,119,76,105,110,101,115,58,32,0
string_2 dq 84,104,101,114,101,32,97,114,101,32,110,111,32,78,101,119,76,105,110,101,115,58,32,0
fstack rb 256
mem rb 8388608
