from core.parser import parse_assembly
from pipeline.controller import Pipeline

FILE = 'programs/array_sum.s'

instructions, initial_memory = parse_assembly(FILE)

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

result = pipeline.registers.read(7)  # t2 = x7
expected = 10 + 20 + 30 + 40 + 50   # 150

print(f"\n=== rezultat ===")
print(f"  t2 (x7) = {result}")
print(f"  asteptat = {expected}")
print(f"  status: {'OK' if result == expected else 'FAIL'}")
print(f"  cicluri: {pipeline.cycle}")
