format ELF64 executable
segment readable executable
    entry start
start:
; INT
mov rax, 69
; PUTC
mov qword [mem+0], rax
lea rsi, [mem+0]
mov rdx, 8
mov rdi, 1
mov rax, 1
syscall
; STOP
mov rax, 60
xor rdi, rdi
syscall
segment readable writable
fstack rb 256
mem rb 8388608
