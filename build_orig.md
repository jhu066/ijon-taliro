**Dependencies**
- C++11 compiler
- Boost
- SDL2
- Flex
- Bison
- CMake

**To build smbc executable**
```
$ git clone https://github.com/RUB-SysSec/ijon-data.git
$ cd ijon-data/SuperMarioBros-C

$ mkdir build
$ cd build
$ cmake ..
$ make

# check for binary named 'smbc'
```

**To run smbc**

Preliminary: download the raw file named 'Super Mario Bros. (JU) (PRG0) [!].nes' from the link below and put it in the same directory of smbc executable (the `build` dir)
https://github.com/seven7bits/7bits/blob/master/app/roms/Super%20Mario%20Bros.%20(JU)%20(PRG0)%20%5B!%5D.nes


To execute smbc with a sample seed:
> usage: `smbc level {trace|video}? < inputfile\n` see example command below:
```
$ ./smbc 0 trace < ../seed/a
```
where:
- `0` is the level number between 0 and 36, find the levels at line 386 of `SuperMarioBros-C/source/Main.cpp`
- `trace` with only input trace, no video support.
- `../seed/a` this is the initial seed IJON uses for fuzzing the `smbc` program. You can also find the set of testcases that can pass each level of the super mario game under `SuperMarioBros-C/payloads` with file names correspond to levels of the game.

Upon successful execution, you should see something like:
```
sefcom@ftc1b:~/ijon/ijon-data/SuperMarioBros-C/build$ ./smbc 0 trace < ../seed/a
got argc 3
run level 0
running mainLoop
0,0
0,0
0,0
0,0
0,0
0,0
0,0
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
40,176
0,0
0,0
0,0
0,0
0,0
0,0
40,176
40,176
42,176
44,176
48,164
52,150
56,138
61,129
67,121
73,115
79,111
85,110
91,111
97,119
103,134
109,150
115,167
121,176
128,176
135,176
143,176
153,176
163,176
173,176
183,176
193,176
203,176
213,176
223,176
233,176
243,176
253,176
262,176
272,176
282,176
292,176
302,176
312,176
done mainLoop
```