fun main() {
    let str = "Hello, SysOpen!";
    syscall(1, 1, str, 15*8);
}
