from core.parser import parse_assembly, ParseError
from pipeline.controller import Pipeline

FILE = 'programs/array_sum.s'

try:
    instructions, initial_memory = parse_assembly(FILE)
except ParseError as e:
    print(e)
    exit(1)

print("=== instructiuni parsate ===")
for i, instr in enumerate(instructions):
    print(f"  PC={i}: {instr}")

print(f"\n=== .data section ===")
for addr, val in initial_memory.items():
    print(f"  mem[{addr:#x}] = {val}")

pipeline = Pipeline(instructions)
for addr, val in initial_memory.items():
    pipeline.memory.write(addr, val)

pipeline.run()

result   = pipeline.registers.read(7)
expected = 10 + 20 + 30 + 40 + 50

print(f"\n=== rezultat ===")
print(f"  cicluri: {pipeline.cycle}")
assert result == expected, f"FAIL: t2={result}, asteptat={expected}"
print(f"  t2 = {result} OK")
