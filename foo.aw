fun print(string) {
    i = 0;
    while (string[i] != 0) {
        putc string[i];
        i = i + 1
    };
}

fun put_one_int(value) {
    value = value + '0'
    putc value
}

fun println(string) {
    print(string)
    putc 10
}

fun main() {
    tab = "Hello, World\n";
    print(tab);
    put_one_int(6);
    put_one_int(9);
    putc 10
    tab = "There are no NewLines: ";
    print(tab);
    tab = "There are no NewLines: ";
    println(tab);
};
