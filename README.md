# RISC-V Performance Analyzer

Tool for simulating and analyzing RISC-V processor performance with detailed cycle-by-cycle execution tracking, in hopes of discovering performance issues such as poor cache exploitation.

## What Does It Do?

Simulates a RISC-V processor cycle-by-cycle to visualize:
- Pipeline flow (IF → ID → EX → MEM → WB)
- Hazard detection and resolution mechanisms
- Performance bottlenecks and optimization opportunities

**Ultimate goal**: Integration into a workflow for code performance testing in computer architecture contexts.

## Quick Start
```bash
python simulator.py programs/fibonacci.s --cache --cache-size 1024 --associativity 4 --verbose
```
## Features

### Implemented features

- **5-Stage Pipeline** (IF/ID/EX/MEM/WB)
  - Data forwarding (EX→ID, MEM→ID, regarding the context)
  - RAW (Read-After-Write) data hazard detection and resolution
  - Branch handling (beq, bne)
  - CPI/IPC calculation

- **Core Components**
  - 32 registers (x0-x31, x0 is **hardwired to zero**)
  - 4KB RAM (word-aligned)
  - Cycle-accurate simulation
  - 4KB stack
    
- **RISC-V RV32I Subset**
  - ALU ops: add, addi, sub, and, or, xor
  - Memory: lw, sw
  - Control: beq, bne

- **Cache simulator**
  - LRU cache replacement policy
  - Write-back and write-through policies
  - Configurable cache size and block size
  - Cache hit/miss tracking, AMAT, hit/miss rates
  - Data validating mechanism

### In progress features
- Cache visualization (hit/miss patterns)
- Assembly parser for .s files (currently using Python-based test programs)

### Planned features
- Branch predictor (2-bit saturating)
- Performance metrics (branch predictor accuracy, et cetera)
- Support for additional RISC-V instructions

**Requirements**: Python 3.10+ (no external dependencies)
## Example Output

From the EX-Stage first shown in the example, we calculate **x3**, the register is then forwarded to the ID-Stage in the same clock cycle, preventing a RAW hazard.

<img width="377" height="467" alt="{079C93B9-0C59-4C3D-B37C-5C404135502D}" src="https://github.com/user-attachments/assets/f1c0a457-d718-46a5-9957-6a1708c55c28" />

```bash
[...the rest of the pipeline]

final state
clock cycles: 33
registers: {2: 3, 3: 5, 4: 5}
status: OK 
```

## Project Structure
```
riscv-cpu-sim/
├── core/           # Instruction, RegisterFile, Memory, Cache
├── pipeline/       # Pipeline stages + controller
├── programs/       # Test programs (.py format)
└── teste/          # Test runner
```

## Tech Stack

- **Language**: Python 3.10+
- **Architecture**: RISC-V RV32I subset
- **Design**: Object-oriented pipeline simulation
- **Dependencies**: None, **for now**
- **To get a grasp on what's going on**: Cristian Rusu's Computer Arhitecutre Lecture
