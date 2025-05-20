# barba
A CPython bytecode optimizer

# Work in progress
- [-] inlining
    - [x] function with args only
    - [ ] functions with args, kwargs, expressions as args, pos only, kwonly, default values, varargs
    - [ ] functions with long body
    - [ ] auto inline short functions
    - [ ] class methods ? (static or not)

# Optimizations to investigate
- [ ] common subexpression elimination
- [ ] strength reduction
- [ ] loop unrolling
- [ ] code motion
- [ ] dead code elimination
- [ ] instruction scheduling
- [ ] constant folding
- [ ] constant propagation
- [ ] vectorization
- [ ] interprocedural analysis
- [ ] loop invariant removal
- [ ] loop jamming
- [ ] loop splitting
- [ ] copy propagation
- [ ] loop fission
- [ ] branch optimization
- [ ] caching
- [ ] peephole optimization
    - [ ] expression tree reshaper
    - [ ] tail merging
    - [ ] code hoisting
- [ ] pipeline optimization
- [ ] alpha and omega motion
- [ ] remove tail recursion
- [ ] register caching over loops
- [ ] loop rotation

- do not return None when not necessary

# References
https://www.youtube.com/watch?v=z0-4EwIFeJo
https://www.youtube.com/watch?v=YY7yJHo0M5I
https://www.youtube.com/watch?v=p57zI4qPVZY&t=1241s
https://www.youtube.com/watch?v=DfXhywRVgN4&t=1442s
https://www.youtube.com/watch?v=XhWvz4dK4ng
https://www.youtube.com/watch?v=cSSpnq362Bk
https://github.com/tonybaloney/Pyjion
https://github.com/tonybaloney/rich-bench
https://github.com/tonybaloney/anti-patterns

https://docs.python.org/3/library/codeop.html
https://docs.python.org/3/library/symtable.html
https://docs.python.org/3/library/py_compile.html
https://docs.python.org/3/library/functions.html#compile
