.data
array:
    .word 10, 20, 30, 40, 50

.text
.globl main
main:
    la   t0, array       # t0 = adresa array
    addi t1, zero, 5     # t1 = lungime array
    addi t2, zero, 0     # t2 = suma
    addi t3, zero, 0     # t3 = i

loop:
    beq  t3, t1, done
    lw   t4, 0(t0)
    add  t2, t2, t4
    addi t0, t0, 4
    addi t3, t3, 1
    beq  zero, zero, loop

done:
    # t2 (x7) = 150
