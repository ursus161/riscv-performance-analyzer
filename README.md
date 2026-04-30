# RISC-V Performance Analyzer

Tool for simulating and analyzing RISC-V processor performance with detailed cycle-by-cycle execution tracking, in hopes of discovering performance issues such as poor cache exploitation.

## What Does It Do?

Simulates a RISC-V processor cycle-by-cycle to visualize:
- Pipeline flow (IF -> ID -> EX -> MEM -> WB)
- Hazard detection and resolution mechanisms
- Branch prediction accuracy and misprediction cost
- Performance bottlenecks and optimization opportunities

**Ultimate goal**: Integration into a workflow for code performance testing in computer architecture contexts.

## Quick Start
```bash
# Basic execution
python run.py programs/array_sum.s

# With branch predictor
python run.py programs/bp_demo2.s --branch-predictor

# With cache simulation
python run.py programs/cache_stress.s --cache --cache-size 1024 --associativity 4

# Verbose (cycle-by-cycle), great for teaching simple pipeline concepts
python run.py programs/array_sum.s --verbose
```

## Features

### Implemented

- **5-Stage Pipeline** (IF/ID/EX/MEM/WB)
  - Data forwarding (EX to ID, MEM to ID)
  - RAW (Read-After-Write) hazard detection and stall insertion
  - Branch handling: beq, bne, blt, bge, bltu, bgeu
  - CPI/IPC calculation

- **Branch Predictor** (A simple Perceptron, in regard to Jimenez & Lin threshold)
  - Global history register (length 8)
  - Per-branch weight table (64 entries) with collision-resistant hashing
  - Accuracy reporting and mispredict count
  - Enabled via `--branch-predictor` flag

- **Cache Simulator**
  - LRU replacement policy
  - Write-back and write-through policies
  - Configurable size, block size, and associativity
  - Hit/miss tracking, AMAT, hit rate

- **Assembly Parser**
  - Parses `.s` files directly (no pre-compilation needed)
  - Two-pass: label resolution + instruction encoding
  - Supports pseudo-instructions: `la`

- **Core Components**
  - 32 registers (x0–x31, ABI names supported, x0 hardwired to zero)
  - 4KB RAM (word-aligned) + 4KB stack
  - Cycle-accurate simulation

- **RISC-V RV32I Subset**
  - R-type: `add`, `sub`, `and`, `or`, `xor`, `sll`, `srl`, `sra`
  - I-type: `addi`, `andi`, `ori`, `xori`, `slti`, `sltiu`, `slli`, `srli`, `srai`
  - Memory: `lw`, `sw`
  - Branches: `beq`, `bne`, `blt`, `bge`, `bltu`, `bgeu`
  - Jumps: `jal`, `jalr`
  - Upper immediate: `lui`, `auipc`

### Planned
- Cache visualization (hit/miss patterns)
- More ways to view the data in regard to each file
- Multiple Branch Predictor policies
- Multi-threaded/multi-process implementation
- Support for M-extension (mul, div)
- Et cetera...

**Requirements**: Python 3.10+ (no external dependencies)

## Example Output

### Pipeline (verbose)
From the EX-Stage first shown in the example, we calculate **x3**, the register is then forwarded to the ID-Stage in the same clock cycle, preventing a RAW hazard.

<img width="377" height="467" alt="{079C93B9-0C59-4C3D-B37C-5C404135502D}" src="https://github.com/user-attachments/assets/f1c0a457-d718-46a5-9957-6a1708c55c28" />

### Branch Predictor
```
stefan@stefan:~/Documents/GitHub/riscv-performance-analyzer$ python run.py programs/bp_demo2.s --branch-predictor
Loaded 43 instructions

==================================================
  Performance Results
==================================================

Execution:
  Total cycles:     1640
  Instructions:     1073
  CPI:              1.53
  IPC:              0.65

Registers:
  x1 = 4
  x2 = 4096
  x5 = 40
  x6 = 40
  x7 = 3
  x28 = 10
  x29 = 10
  x30 = 8
  x31 = 8

Branch Predictor :
  Total branches:   655
  Corecte:          588 (89.8%)
  Mispredictions:   67
==================================================
```

Without `--branch-predictor`, running the bp_demo2.s file, the pipeline stalls on every branch (1804 cycles, CPI 1.68).
With the perceptron predictor, 89.8% of branches are predicted correctly, saving 164 cycles.

## Project Structure
```
riscv-performance-analyzer/
├── core/
│   ├── instruction.py      # Instruction model and validation
│   ├── parser.py           # Two-pass assembly parser
│   ├── registers.py        # Register file
│   ├── memory.py           # RAM + stack
│   ├── cache.py            # Cache simulator
│   └── branch_predictor.py # Perceptron predictor
├── pipeline/
│   ├── stages.py           # IF, ID, EX, MEM, WB stage logic
│   └── controller.py       # Pipeline controller, hazard unit
├── programs/               # RISC-V assembly test programs (.s)
├── cache_compare.py        # Cache policy comparison utility
└── run.py                  # Entry point
```

## Tech Stack

- **Language**: Python 3.10+
- **Architecture**: RISC-V RV32I subset
- **Design**: Object-oriented pipeline simulation
- **Dependencies**: None

- **References**: Intro to RISC-V and theoretical materials :https://cs.unibuc.ro/~crusu/asc/Arhitectura%20Sistemelor%20de%20Calcul%20(ASC)%20-%20Laborator%20Partea%200x02.pdf https://cs.unibuc.ro/~crusu/asc/lectures.html ;
                  A great paper on Branch Predictors, which I've enjoyed: https://www.cs.utexas.edu/~lin/papers/tocs02.pdf ;
                  For getting your feet wet on cache replacement policies: https://www.geeksforgeeks.org/computer-organization-architecture/cache-replacement-policies/
               