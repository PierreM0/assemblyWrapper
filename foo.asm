section .data
     global_mem:
         align 4096
         times 8388608 db 0
section .text
    global _start
_start:
; ARRAYNODE
mov qword [global_mem+0], 72
mov qword [global_mem+8], 101
mov qword [global_mem+16], 108
mov qword [global_mem+24], 108
mov qword [global_mem+32], 111
mov qword [global_mem+40], 44
mov qword [global_mem+48], 32
mov qword [global_mem+56], 87
mov qword [global_mem+64], 111
mov qword [global_mem+72], 114
mov qword [global_mem+80], 108
mov qword [global_mem+88], 100
mov qword [global_mem+96], 10
mov qword [global_mem+104], 0
lea rax, [global_mem+0]
; ASSIGN
mov [global_mem+112], rax
.l1:
; INT
mov rax, 0
; ASSIGN
mov [global_mem+120], rax
.l2:
; IF
.L0:
; INT
mov rax, 0
push rax
; INT
mov rax, 0
pop rbx
; EQ
cmp rax, rbx
sete al
movzx rax, al
cmp rax, 0
je .L1
; INT
mov rax, 69
; PUTC
mov [global_mem+128], rax
lea rsi, [global_mem+128]
mov rdx, 8
mov rdi, 1
mov rax, 1
syscall
; IDENTIFIER
mov rax, [global_mem+120]
push rax
; INT
mov rax, 8
pop rbx
; ADD
add rax, rbx
; ASSIGN
mov [global_mem+120], rax
.L1:
; STOP
mov rax, 60
xor rdi, rdi
syscall
