fun test_assign_int() {
    let a;
    a = 10;
    if (a != 10) putc '1';
    a = 10 + 10;
    if (a != 20) putc '1';
    a = 10 * 10;
    if (a != 100) putc '1';
}

fun test_assign_char() {
    let a;
    a = '0';
    if (a != 48) putc '2';
    a = '0' + '0';
    if (a != 96) putc '2';
    a = '0' * '0';
    if (a != 2304) putc '2';
}

fun test_assign_string() {
    let str;
    str = "HELLO";
    if (str[0] != 'H') putc '3';
    if (str[1] != 'E') putc '3';
    if (str[2] != 'L') putc '3';
    if (str[3] != 'L') putc '3';
    if (str[4] != 'O') putc '3';
}

fun test_assign_tab() {
    let tab;
    tab = [0, 1, 2];
    if (tab[0] != 0) putc '4';
    if (tab[1] != 1) putc '4';
    if (tab[2] != 2) putc '4';
    tab[1] = 2;
    if (tab[0] != 0) putc '4';
    if (tab[1] != 2) putc '4';
    if (tab[2] != 2) putc '4';
}

fun main() {
    test_assign_int();
    test_assign_char();
    test_assign_string();
}
