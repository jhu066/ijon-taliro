**Step 1**: Make sure you can build and run the original version of `smbc` executable. See `build_orig.md` for detailed instructions.

**Step 2**: Backup the `Main.cpp` under `SuperMarioBros-C/source`, and use the Main.cpp in this repo instead.

**Step 3**: Rebuild `smbc` by the following command:
```
$ cd SuperMarioBros-C/source/build
$ cmake ..
$ make
```

**Step 4**: Test the new `smbc` using the test case (`test.test`) in this repo. Make sure the file `Super Mario Bros. (JU) (PRG0) [!].nes` and `smbc` are under the same directory.
```
$ ./smbc 0 trace < test.test
```

You should see print out as below:
```
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
40,176
40,176
40,176
40,176
40,176
40,176
40,176
41,176
43,176
45,176
48,176
52,176
56,176
61,176
66,176
72,176
78,176
84,176
90,176
96,176
102,176
108,176
114,176
120,176
126,176
132,176
138,176
144,176
150,176
156,176
162,176
168,176
174,176
180,176
186,176
192,176
198,176
204,176
210,176
216,176
222,176
228,176
234,176
240,176
246,168
252,153
257,141
263,144
269,153
274,168
279,176
282,176
284,176
283,176
281,168
281,153
280,144
281,142
283,147
286,159
290,160
295,152
301,151
307,157
313,170
320,176
327,171
334,152
341,140
348,147
356,162
363,176
370,176
376,176
381,176
387,176
393,176
399,176
405,176
411,176
417,176
423,176
429,176
434,176
433,176
432,176
429,176
426,176
422,176
417,160
412,147
406,135
400,126
396,118
396,112
done mainLoop
```



**Explain I/O between ijon and taliro**

The testcase for smbc would be a sequence of lines, each line is in the form of `x,y` where:
- `x`: 1 for jump, 0 for no;
- `y`: 1 for go right, 0 for no;


Valid lines include:
```
0,0 # no action
1,0 # jump
0,1 # go right
1,1 # jump and go right at the same time
```

Each frame process one line. So if taliro decides we should continuously go right for several seconds, the input should have several lines of `0,1`.

The output for executing `smbc` with a given testcase is the same as the example output in `Step 4` where the coordinates `(i, j)` is printed, `i` is the position in the horizontal direction (we want this to be as high as possible) and `j` is the position in the vertical direction.
