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

fun print_int(integer) {
  if (integer == 0) putc '0';

  const MAX_INT_PRINTABLE_SIZE 30;
  let tab[MAX_INT_PRINTABLE_SIZE];

  let i = 0;
  while (integer != 0) {
    tab[i] = integer %  10;
    i = i+1;
  
    integer = integer / 10;
  }
 
  while (i != 0) {
      putc(tab[i-1] + '0');
      i = i-1;
  }
}

println_int(integer) {
    print_int(integer);
    putc 10;
  }
