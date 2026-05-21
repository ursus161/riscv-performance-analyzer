.data

.text
.global main

# Suma 0+1+2+...+99 = 4950
# bne back: T x99, NT x1 — un singur branch, pattern simplu, BP invata in ~8 iteratii
#
# Fara BP: ~99 branch_flush_cycles (add de la done: e adus gresit la fiecare iteratie taken)
# Cu BP  : ~11 branch_flush_cycles (warm-up ~9 + 1 mispredict final)

main:
    addi t0, zero, 0     # i = 0
    addi t1, zero, 100   # N = 100
    addi t2, zero, 0     # suma = 0

loop:
    add  t2, t2, t0      # suma += i
    addi t0, t0, 1       # i++
    bne  t0, t1, loop    # T x99, NT x1 — BP invata "T" rapid

done:
    add  t3, t2, zero    # t3 = suma (4950) — adusa gresit in pipeline fara BP
