fun main() {
    let tab[4];

    let tab2;
    tab2 = [1, 2, 3, 4];

    if (tab2[0] != 1) putc '1';
    if (tab2[1] != 2) putc '2';
    if (tab2[2] != 3) putc '3';
    if (tab2[3] != 4) putc '4';

    tab[0] = 1;
    if (tab[0] != 1) putc '1';
    tab[1] = 2;
    if (tab[1] != 2) putc '2';
    tab[2] = 3;
    if (tab[2] != 3) putc '3';
    tab[3] = 4;
    if (tab[3] != 4) putc '4';

}