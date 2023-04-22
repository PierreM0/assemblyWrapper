fun test_putc_add_int_char() {
    putc 4 + '0';
    putc 4 + 3 + 2 + 1 + '0';
}

fun test_putc_char() {
    putc 'H';
    putc 'e';
}

fun test_putc_add_int() {
    putc 35 + 35;
}

fun test_putc_int() {
    putc 34;
    putc 35;
}

fun main() {
    test_putc_int();
    test_putc_add_int();
    test_putc_char();
    test_putc_add_int_char();
}
