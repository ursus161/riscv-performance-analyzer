
from core.instruction import Instruction
from pipeline.controller import Pipeline

instructions = [
    Instruction("addi", rd=1, rs1=0, imm=5),
    Instruction("beq", rs1=0, rs2=0, imm=2),
    Instruction("addi", rd=2, rs1=0, imm=10),
    Instruction("addi", rd=3, rs1=0, imm=20),
]

pipeline = Pipeline(instructions)
pipeline.run()

stats = pipeline.get_performance_stats()
print(f"Total instructions: {stats['total_instructions']}")
print(f"CPI: {stats['cpi']}")
