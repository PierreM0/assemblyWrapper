const O_ACCMODE	  00000003;
const O_RDONLY	  00000000;
const O_WRONLY	  00000001;
const O_RDWR		  00000002;
const O_CREAT		  00000100;
const O_EXCL		  00000200;
const O_NOCTTY	  00000400;
const O_TRUNC		  00001000;
const O_APPEND	  00002000;
const O_NONBLOCK	00004000;
const O_DSYNC		  00010000;
const O_FASYNC		00020000;
const O_DIRECT	  00040000;
const O_LARGEFILE	00100000;
const O_DIRECTORY	00200000;
const O_NOFOLLOW	00400000;
const O_NOATIME	  01000000;
const O_CLOEXEC	  02000000;
const O_PATH		  10000000;

fun read(file_descriptor, buff, len) {
    syscall(0, file_descriptor, buff, len);
}

fun open(file_name, flags) {
    return syscall(2, file_name, flags, 0);
}

fun close(file_descriptor) {
    syscall(3, file_descriptor);
}

fun print(str) {
    let i; i = 0;
    while (str[i] != 0) {
        putc(str[i]);
        i = i + 1; 
    }
}
