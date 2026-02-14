# face fib(10)

addi sp, sp, -16
sw s0, 0(sp)
sw s1, 4(sp)

addi a0, zero, 10
addi s0, zero, 0
addi s1, zero, 1
addi t0, zero, 2

loop:
    add t1, s0, s1
    add s0, s1, zero
    add s1, t1, zero
    addi t0, t0, 1
    bne t0, a0, loop

add a0, s1, zero

lw s0, 0(sp)
lw s1, 4(sp)
addi sp, sp, 16
