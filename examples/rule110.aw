fun print_int(i) {
    let var;
    var = '0' + i;
    putc var;
}

fun print_tab(tab, tab_size) {
    let i;
    i = 0;
    while (i != tab_size) {
        print_int(tab[i]);
        i = i+1;
    }
    putc 10;
}

fun main() {
    let tab;
    let tab_size;
    let iterations;

    iterations = 19;

    tab = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1];
    tab_size = 20;

    let line;

    line = 0;


    print_tab(tab, tab_size);

    while (line != iterations) {
        let i;
        i = 0;

        let new_tab;
        new_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        while (i != 20) {
            new_tab[i] = tab[i];
            i = i + 1;
        }

        i = 0;
        while (i != 19) {
        if (tab[i-1] != 1) {
            if (tab[i] != 1) {
                if (tab[i+1] != 1) {
                    new_tab[i] = 0;
                }
                if (tab[i+1] == 1) {
                    new_tab[i] = 1;
                }
            }
            if (tab[i] == 1) {
                if (tab[i+1] != 1) {
                }
                if (tab[i+1] == 1) {
                    new_tab[i] = 1;
                }
            }
        }
        if (tab[i-1] == 1) {
            if (tab[i] != 1) {
                if (tab[i+1] != 1) new_tab[i] = 0;
                if (tab[i+1] == 1) new_tab[i] = 1;
            }
            if (tab[i] == 1) {
                if (tab[i+1] != 1) new_tab[i] = 1;
                if (tab[i+1] == 1) new_tab[i] = 0;
            }
        }
        i = i + 1;
        }
        print_tab(new_tab, tab_size);

        i = 0;
        while (i != 20) {
            tab[i] = new_tab[i];
            i = i + 1;
        }

        line = line + 1;
    }
}
