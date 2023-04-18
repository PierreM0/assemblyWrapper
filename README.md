# AssemblyWrapper

Simple python wrapper for assembly.

# How to use:
```console
$ ./main.py foo.aw foo
$ ./foo
```
It will generate an assembly file: `foo.asm` and an object file: `foo.o`

### Supported functionalities:
- Variable: (integers and strings)
```
foo = 34  
bar = "35"
```
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

- Operators:
  - `+`
  - `*`
  - `!=`
  - `==`

## ROADMAP: 
- [ ] Testing it 
- [ ] Make the code coherent
- [ ] Make it turing complete
- [ ] Make it fun to write