.data

.text
.global main
main:
    addi t0, zero, 0     # i = 0
    addi t1, zero, 50    # limita = 50
    addi t2, zero, 0     # suma = 0

loop:
    beq  t0, t1, done    # iesire: not-taken de 50x, taken o singura data
    addi t2, t2, 1       # suma++
    addi t0, t0, 1       # i++
    beq  zero, zero, loop  # salt inapoi: luat de 50x teoretic BP invata rapid

done:
    # t2 (x7) = 50
