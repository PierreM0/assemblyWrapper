fun test_shift_left() {
    let var;
    let a;
    var = 2;
    a = var << 1;
    if (a != 4) putc '1';
    a = var << 2;
    if (a != 8) putc '1';
    a = var << 3;
    if (a != 16) putc '1';
    a = var << 4;
    if (a != 32) putc '1';
}

fun test_shift_right() {
    let var;
    let a;
    var = 32;
    a = var >> 1;
    if (a != 16) putc '2';
    a = var >> 2;
    if (a != 8) putc '2';
    a = var >> 3;
    if (a != 4) putc '2';
    a = var >> 4;
    if (a != 2) putc '2';
}


fun main() {
    test_shift_left();
    test_shift_right();
}