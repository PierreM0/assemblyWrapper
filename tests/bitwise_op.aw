fun test_or() {
    let var;
    let a;
    var = 9;
    a = var | 1;
    if (a != 9) putc '1';
    a = var | 2;
    if (a != 11) putc '1';
    a = var | 3;
    if (a != 11) putc '1';
    a = var | 4;
    if (a != 13) putc '1';
}

fun test_and() {
    let var;
    let a;
    var = 9;
    a = var & 1;
    if (a != 1) putc '2';
    a = var & 2;
    if (a != 0) putc '2';
    a = var & 3;
    if (a != 1) putc '2';
    a = var & 4;
    if (a != 0) putc '2';
}


fun main() {
    test_or();
    test_and();
}