.data
result: .word 0

.text
.globl main
main:
    addi t0, zero, 6      # limita loop     
    addi t1, zero, 0      # suma = 0
    addi t2, zero, 1      # i = 1

loop:
    bge  t2, t0, done     # if i >= 6 -> done
    add  t1, t1, t2       # suma += i
    addi t2, t2, 1        # i++
    beq  zero, zero, loop

done:
    # t1 = 1+2+3+4+5 = 15
    slli t3, t1, 1        # t3 = 30  (shift left = x2)
    add  t4, t1, t3       # t4 = 45
    sub  t5, t4, t1       # t5 = 30
    slt  t6, t1, t4       # t6 = 1   (15 < 45)
    la   t0, result
    sw   t1, 0(t0)        # scrie 15 in memorie -> apare in Memory panel
