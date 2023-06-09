# AssemblyWrapper

Simple python wrapper for assembly.

# How to use:
```console
$ ./main.py examples/rule110.aw rule110
$ ./rule110
```
It will generate an assembly file: `foo.asm` and an object file: `foo.o`

# Dependencies:
- [fasm](flatassembler.net)
- ld
- python3.11

### Supported functionalities:
- Variable: (integers and strings)
```
foo = 34  
bar = "35
```
Characters ares integers:
`foo = 'E' <=> foo = 69`.
- Tables:
```
table = [34, 35, 69, 361, 420]
```
- While loops:
```
a = 0;
b = 9;
while (a != b) {
    a = a + 1;
};

>>> a == 9
```
- If statements :
```
a = 0;
b = 9;
if (a != b) {
    a = a + 1;
};

>>> a == 1
```
- (Verry limited) Functions:
```
fun a(value) {
  putc value 
}
```
A function cannot return anything for the moment

- Operators:
  - `+`
  - `*`
  - `!=`
  - `==`

## ROADMAP: 
- [ ] Testing it 
- [x] Make it turing complete
- [ ] Make the code coherent
- [ ] Make it fun to write