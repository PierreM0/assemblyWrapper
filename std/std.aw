fun print(str) {
    let i; i = 0;
    while (str[i] != 0) {
        putc(str[i]);
        i = i + 1; 
    }
}

fun println(str) {
    print(str);
    putc 10;
}


