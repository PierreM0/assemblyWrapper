fun print_stars_spaces(i) {
    let tab;
    tab = [' ', '*'];
    putc (tab[i]);
}

fun main() {
    const BOARD_CAP 100;

    let board[BOARD_CAP];

    board[BOARD_CAP -2] = 1;

    let i; i=0;
    while ( i != BOARD_CAP-3) {
        board[i] = 0;
        i = i + 1;
    }
    i = 0;

    while (i != BOARD_CAP -2) {
        let j; j = 0;
        while (j != BOARD_CAP) {

            print_stars_spaces(board[j]);
            j = j + 1;
        }

        putc 10;

        let pattern;
        pattern = (board[0] << 1) | board[1];
        j=1;
        while (j != (BOARD_CAP-1)) {
            pattern = ((pattern << 1) & 7) | board[j+1];
            board[j] = (110 >> pattern) & 1 ;

            j = j + 1;


        }

        i = i + 1;
    }
}