.data

.text
.global main

main:
    jal  ra, tight_loop
    jal  ra, nested_loops
    jal  ra, alternating
    jal  ra, mixed_cond
    beq  zero, zero, done

# beq exit: NT x100, T x1  -> BP invata NT rapid, 1 mispredict la final
# beq back: T x100          -> BP invata T rapid, 0 mispredicts dupa warm-up

tight_loop:
    addi t0, zero, 0
    addi t1, zero, 100
tl_loop:
    beq  t0, t1, tl_done
    addi t0, t0, 1
    beq  zero, zero, tl_loop
tl_done:
    jalr zero, ra, 0


nested_loops:
    addi t3, zero, 0
    addi t4, zero, 10
nl_outer:
    beq  t3, t4, nl_done
    addi t5, zero, 0
    addi t6, zero, 8
nl_inner:
    beq  t5, t6, nl_iexit
    addi t5, t5, 1
    beq  zero, zero, nl_inner
nl_iexit:
    addi t3, t3, 1
    beq  zero, zero, nl_outer
nl_done:
    jalr zero, ra, 0

alternating:
    addi t0, zero, 0
    addi t1, zero, 40
alt_loop:
    beq  t0, t1, alt_done
    andi t2, t0, 1
    beq  t2, zero, alt_even    # T cand i par (0,2,4,...), NT cand impar
    beq  zero, zero, alt_cont  # ramura impar: sare peste nop
alt_even:
    addi zero, zero, 0         # nop ramura para
alt_cont:
    addi t0, t0, 1
    beq  zero, zero, alt_loop
alt_done:
    jalr zero, ra, 0

# branch luat numai cand i % 4 == 0 
# bne "mc_skip": NT x3, T x1 repetat -> pattern NNNTNNNTNNN

mixed_cond:
    addi t0, zero, 0
    addi t1, zero, 40
    addi t3, zero, 0
mc_loop:
    beq  t0, t1, mc_done
    andi t2, t0, 3
    bne  t2, zero, mc_skip     # NT x3, T x1 per ciclu de 4
    addi t3, t3, 1             # contor branch-uri luate (=10 la final)
mc_skip:
    addi t0, t0, 1
    beq  zero, zero, mc_loop
mc_done:
    jalr zero, ra, 0

done:
    addi zero, zero, 0
