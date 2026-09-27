# RISC-V Performance Analyzer

Tool for simulating and analyzing RISC-V processor performance with detailed cycle-by-cycle execution tracking, in hopes of discovering performance issues such as poor cache exploitation.

## What Does It Do?

Simulates a RISC-V processor cycle-by-cycle to visualize:
- Pipeline flow (IF -> ID -> EX -> MEM -> WB)
- Hazard detection and resolution mechanisms
- Branch prediction accuracy and misprediction cost
- Performance bottlenecks and optimization opportunities

**Ultimate goal**: Integration into a workflow for code performance testing in computer architecture contexts.

## Architecture

### Pipeline

5-stage in-order pipeline: IF → ID → EX → MEM → WB. Tick order is WB→MEM→EX→ID→IF so downstream results are visible to upstream stages within the same cycle.

- **Data forwarding**: EX→ID and MEM→ID paths. Detects RAW hazards and inserts stalls only when forwarding is impossible (load-use).
- **Branch resolution**: branches resolve in EX. On misprediction, IF and ID are flushed (2-cycle penalty). With the predictor enabled, the BTB provides a predicted target and the perceptron votes taken/not-taken before EX.
- **PC**: stored as instruction index, not byte address. Branch targets are instruction-index offsets.

### Branch Predictor

Perceptron predictor following Jimenez & Lin (2002):
- Global history register of length 8
- 64-entry weight table, per-entry weights vector of length 9 (1 bias + 8 history bits)
- Prediction: dot product of weights · history; threshold = floor(1.93 * 8 + 14)
- Training: weights updated on misprediction or when output is within threshold (perceptron learning rule)
- Hashing: PC folded into table index via XOR to reduce aliasing

### Cache

Set-associative with configurable parameters:
- Size, line size (fixed 16B), associativity
- LRU replacement via recency list per set
- Write-back (dirty bit + writeback on eviction) and write-through policies
- Tracks hits, misses, writebacks; reports hit rate and AMAT (assuming 10-cycle miss penalty)

### Web Stack

```
browser → nginx:80
            ├── /api/* → proxy_pass → uvicorn:8000 (FastAPI)
            └── /*     → static dist/ (React SPA)
```

Two containers: `docker-api` (python:3.12-slim) and `docker-frontend` (nginx:alpine, multi-stage build — Node build stage discarded, only `dist/` copied into final image). API container has no exposed ports; only reachable from nginx via Docker's internal network.

Session management: step-mode creates a `Pipeline` instance stored server-side by UUID. Full-run and compare endpoints are stateless.

`/compare` runs 30 pipeline variants (5 sizes x 3 associativities x 2 write policies) against a no-cache baseline and returns all stats in one response.

Hard cap of 100k cycles server-side regardless of client input, as DoS mitigation.

## Quick Start

### Docker
```bash
sudo docker compose -f docker/docker-compose.yml up --build
```
Open `http://localhost`.

### CLI
```bash
python run.py programs/array_sum.s
python run.py programs/bp_demo2.s --branch-predictor
python run.py programs/cache_stress.s --cache --cache-size 1024 --associativity 4
python run.py programs/array_sum.s --verbose
```

## RV32I Subset

| Type | Instructions |
|------|-------------|
| R | `add` `sub` `and` `or` `xor` `sll` `srl` `sra` |
| I | `addi` `andi` `ori` `xori` `slti` `sltiu` `slli` `srli` `srai` |
| Load/Store | `lw` `sw` |
| Branch | `beq` `bne` `blt` `bge` `bltu` `bgeu` |
| Jump | `jal` `jalr` |
| Upper imm | `lui` `auipc` |

Parser is two-pass: first pass resolves labels, second encodes instructions. No external assembler required.

## Project Structure
```
riscv-performance-analyzer/
├── core/
│   ├── instruction.py      # Instruction model
│   ├── parser.py           # Two-pass assembly parser
│   ├── registers.py        # 32-entry register file, x0 hardwired
│   ├── memory.py           # Word-aligned RAM + cache integration
│   ├── cache.py            # Set-associative cache
│   └── branch_predictor.py # Perceptron + BTB
├── pipeline/
│   ├── stages.py           # IF, ID, EX, MEM, WB
│   └── controller.py       # Hazard detection, forwarding, pipeline control
├── api/
│   └── main.py             # FastAPI: /simulate /session /compare
├── frontend/               # React 18 + Vite + Tailwind
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   └── nginx.conf
├── programs/               # RV32I assembly test programs
├── cache_compare.py        # CLI cache sweep utility
└── run.py                  # CLI entry point
```

## Tech Stack

- **Simulator**: Python 3.10+, zero dependencies
- **Backend**: FastAPI, uvicorn, pydantic v2
- **Frontend**: React 18, Vite, Tailwind CSS
- **Infrastructure**: Docker, nginx reverse proxy

## References

- [Intro to RISC-V](https://cs.unibuc.ro/~crusu/asc/Arhitectura%20Sistemelor%20de%20Calcul%20(ASC)%20-%20Laborator%20Partea%200x02.pdf)
- [Computer Architecture lectures](https://cs.unibuc.ro/~crusu/asc/lectures.html)
- [Jimenez & Lin — Dynamic Branch Prediction with Perceptrons (2002)](https://www.cs.utexas.edu/~lin/papers/tocs02.pdf)
- [Cache replacement policies](https://www.geeksforgeeks.org/computer-organization-architecture/cache-replacement-policies/)
