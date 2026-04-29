.data
array:
    .word 1, 2, 3, 4, 5, 6, 7, 8
    .word 9, 10, 11, 12, 13, 14, 15, 16
    .word 17, 18, 19, 20, 21, 22, 23, 24
    .word 25, 26, 27, 28, 29, 30, 31, 32

.text
.globl main
main:
    addi t1, zero, 32    # N = 32 elemente
    addi t5, zero, 2     # numar de treceri
    addi t6, zero, 0     # contor treceri
    addi t2, zero, 0     # suma

outer:
    beq  t6, t5, done
    la   t0, array
    addi t3, zero, 0     # i = 0

inner:
    beq  t3, t1, end_inner
    lw   t4, 0(t0)
    add  t2, t2, t4
    addi t0, t0, 4
    addi t3, t3, 1
    beq  zero, zero, inner

end_inner:
    addi t6, t6, 1
    beq  zero, zero, outer

done:
    # t2 = suma array-ului * 2 treceri = 1056
