from core.instruction import Instruction
from pipeline.controller import Pipeline
from pipeline.stages import WBStage

print("="*50)
print("test raw hazard")
print("="*50)

instructions = [
    Instruction("addi", rd=1, rs1=0, imm=10), #addi x1,x0,10
    Instruction("add", rd=2, rs1=1, rs2=1),   #add x2, x1, x1
]

pipeline = Pipeline(instructions)
pipeline.run()

print("\nvreau: x1=10, x2=20")
print(f"regs: x1={pipeline.registers.read(1)}, x2={pipeline.registers.read(2)}")
print(f"Result: {'hazardul RAW nu a fost handled!' if pipeline.registers.read(2) == 0 else 'OK'}")