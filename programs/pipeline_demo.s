.data
val: .word 42

.text
.globl main
main:
    la   t0, val        # t0 = adresa lui val
    lw   t1, 0(t0)      # t1 = 42  (load)
    add  t2, t1, t1     # stall — t1 nu e gata inca (load-use hazard)
    add  t3, t2, t1     # forwarding acopera (fara stall)
    addi t4, t3, 1      # forwarding acopera (fara stall)
