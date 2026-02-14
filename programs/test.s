
addi x1, x0, 0
addi x2, x0, 10

loop:
addi x1, x1, 1
bne x1, x2, loop

# x1 tb sa fie 10 ; acest comentariu are scop de test pentru parser