.data
# doi vectori separati, plasati strategic
# daca cache line size = 16B si ai 16 seturi intr-un cache de 256B direct-mapped,
# fiecare element din array1[i] si array2[i] vor lupta pentru acelasi set
# practic forteaza conflict misses
array1:
    .word 1, 2, 3, 4, 5, 6, 7, 8
    .word 9, 10, 11, 12, 13, 14, 15, 16
    .word 17, 18, 19, 20, 21, 22, 23, 24
    .word 25, 26, 27, 28, 29, 30, 31, 32
    .word 33, 34, 35, 36, 37, 38, 39, 40
    .word 41, 42, 43, 44, 45, 46, 47, 48
    .word 49, 50, 51, 52, 53, 54, 55, 56
    .word 57, 58, 59, 60, 61, 62, 63, 64

.space 256  # spatiu exact = dimensiune cache tipica
            # asta face ca array1[0] si array2[0] sa mapeze la acelasi set in direct-mapped
            # practic garantez conflict misses

array2:
    .word 65, 66, 67, 68, 69, 70, 71, 72
    .word 73, 74, 75, 76, 77, 78, 79, 80
    .word 81, 82, 83, 84, 85, 86, 87, 88
    .word 89, 90, 91, 92, 93, 94, 95, 96
    .word 97, 98, 99, 100, 101, 102, 103, 104
    .word 105, 106, 107, 108, 109, 110, 111, 112
    .word 113, 114, 115, 116, 117, 118, 119, 120
    .word 121, 122, 123, 124, 125, 126, 127, 128

.text
.globl main
main:
    # TRECEREA 1: pattern de thrashing - alternez intre array1 si array2
    # in direct-mapped, fiecare acces din array2 da afara corespondentul din array1
    # in 2-way/4-way, pot coexista amandoi (deci asociativitatea conteaza mult)
    
    addi t5, zero, 8         # 8 iteratii de thrashing ca sa fie evident
    addi t6, zero, 0         # contor iteratii
    addi s0, zero, 0         # suma totala (pt verificare ca merge bine)

thrash_outer:
    beq  t6, t5, thrash_done
    
    # citesc tot array1 - incarc cache-ul
    la   t0, array1
    addi t1, zero, 64        # 64 de words
    addi t3, zero, 0         # index
    
thrash_a1:
    beq  t3, t1, thrash_a1_done
    lw   t4, 0(t0)           # load din array1 -> cache se incarca
    add  s0, s0, t4
    addi t0, t0, 4
    addi t3, t3, 1
    beq  zero, zero, thrash_a1

thrash_a1_done:
    # acum citesc tot array2
    # daca cache e mic si direct-mapped, da afara TOT ce era din array1
    # daca e 4-way, pot sta amandoi linistiti in cache
    la   t0, array2
    addi t1, zero, 64
    addi t3, zero, 0
    
thrash_a2:
    beq  t3, t1, thrash_a2_done
    lw   t4, 0(t0)           # load din array2 -> evict array1 in direct-mapped
    add  s0, s0, t4
    addi t0, t0, 4
    addi t3, t3, 1
    beq  zero, zero, thrash_a2

thrash_a2_done:
    # repet de 8 ori
    # daca cache e mic, fiecare iteratie = fresh misses
    # daca cache e mare cu asociativitate, temporal locality salveaza situatia
    addi t6, t6, 1
    beq  zero, zero, thrash_outer

thrash_done:
    # TRECEREA 2: interleaved access - mai rau decat thrashing
    # alternare la nivel de element: array1[0], array2[0], array1[1], array2[1], ...
    # asta maximizeaza conflict misses chiar si in set-associative
    # e cel mai nasol pattern pt cache
    
    addi t1, zero, 64        # 64 elemente per array
    addi t3, zero, 0         # index
    
interleave_loop:
    beq  t3, t1, interleave_done
    
    # calculez offset = i * 4 (word-aligned)
    add  t2, t3, t3          # t2 = i*2
    add  t2, t2, t2          # t2 = i*4
    
    # acces array1[i]
    la   t0, array1
    add  t0, t0, t2
    lw   t4, 0(t0)           # incarc linia in cache
    add  s0, s0, t4
    
    # imediat dupa: acces array2[i]
    # conflict garantat linia de la array1[i] probabil evicted imediat
    la   t0, array2
    add  t0, t0, t2
    lw   t4, 0(t0)
    add  s0, s0, t4
    
    addi t3, t3, 1
    beq  zero, zero, interleave_loop

interleave_done:
    # TRECEREA 3: strided access prin ambele
    # sar peste 8 elemente = 32 bytes
    # asta testeaza spatial locality - o stric intentionat
    # daca aveam prefetcher, ar ajuta aici (dar nu am)
    
    la   t0, array1
    addi t1, zero, 8         # doar 8 accese, dar distribuite
    addi t3, zero, 0
    
stride_loop:
    beq  t3, t1, done
    lw   t4, 0(t0)
    add  s0, s0, t4
    addi t0, t0, 32          # +8 words = sar o gramada de cache lines
    addi t3, t3, 1
    beq  zero, zero, stride_loop

done:
    # s0 = suma finala
    # daca programul e corect, trebuie sa fie o valoare consistenta
    # pt debugging: (1+2+...+64)*8 iteratii thrash + (65+...+128)*8 + interleaved + stride