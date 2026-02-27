
# Sum array of 32 elements to stress cache


addi sp, sp, -16
sw s0, 0(sp)
sw s1, 4(sp)

addi s0, zero, 1024     # base address = 1024
addi s1, zero, 32       # array size = 32 elements
addi t0, zero, 0        # counter i = 0
addi a0, zero, 0        # sum = 0

write_loop:
    beq t0, s1, write_done


    add t1, t0, t0          # t1 = i*2
    add t1, t1, t1          # t1 = i*4
    add t2, s0, t1          # t2 = base + i*4

    # Value = i + 1
    addi t3, t0, 1

    sw t3, 0(t2)

    addi t0, t0, 1
    beq zero, zero, write_loop

write_done:

    addi t0, zero, 0

read_loop:
    beq t0, s1, read_done

    add t1, t0, t0
    add t1, t1, t1
    add t2, s0, t1

    lw t3, 0(t2)

    # Add to sum
    add a0, a0, t3

    addi t0, t0, 1
    beq zero, zero, read_loop

read_done:
    lw s0, 0(sp)
    lw s1, 4(sp)
    addi sp, sp, 16
