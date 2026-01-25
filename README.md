# RISC-V Pipeline Analyzer

Simulator de procesor RISC-V in Python cu pipeline, cache si branch prediction.

## Ce face

Simuleaza un procesor RISC-V ciclu cu ciclu si arata exact unde se pierde timpul:
- Vizualizare pipeline (IF → ID → EX → MEM → WB)
- Cache hits/misses
- Predictie branch-uri
- Statistici de performanta

## Rulare
```bash
python test_if.py
```

## Features in progress

- **Pipeline 5 stage-uri** cu detectare hazards
- **Cache simulator** (LRU, configurable)
- **Branch predictors** (2-bit, maybe perceptron)
- **Stats** (CPI, hit rate, accuracy)

## Output Exemplu
```
Cycle 10:
Pipeline: [lw] [add] [addi] [ ] [ ]
Cache: 0x1004 → MISS (85% hit rate)
Branch: TAKEN ✓ (92% accuracy)

Stats:
- CPI: 1.8
- Cache hits: 85%
- Stalls: 15
```

## Structura
```
riscv-cpu-sim/
├── core/           # Instructiuni, registre, memorie
├── pipeline/       # Pipeline stages + hazards
├── cache/          # Cache + LRU
├── predictors/     # Branch predictors
└── programs/       # Fisiere .s de test
```

## Tech Stack

Python 3.10+ | RISC-V ISA (subset)

