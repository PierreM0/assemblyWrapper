fun test_div() {
    let a; a = 2;
    let var;
    var = 1 / a;
    if (var != 0) putc '1';
    var = 2 / a;
    if (var != 1) putc '3';
    var = 3 / a;
    if (var != 1) putc '5';
    var = 4 / a;
    if (var != 2) putc '7';
}

fun test_mod() {
    let a; a = 4;
    let var;
    var = 1 % a;
    if (var != 1) putc '2';
    var = 2 % a;
    if (var != 2) putc '4';
    var = 3 % a;
    if (var != 3) putc '6';
    var = 4 % a;
    if (var != 0) putc '8';
}

fun main() {
    test_div();
    test_mod();
}
