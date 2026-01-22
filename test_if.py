from core.instruction import Instruction
from core.registers import RegisterFile
from pipeline.stages import IFStage, IDStage


class MockPipeline:
    def __init__(self, instructions):
        self.instructions = instructions
        self.pc = 0
        self.registers = RegisterFile()


        self.stages = {
            'IF': IFStage(self),
            'ID': IDStage(self)
        }


instructions = [
    Instruction("addi", rd=1, rs1=0, imm=5), #addi x1,x0,5
    Instruction("add", rd=2, rs1=1, rs2=1)   #add x2,x1,x1
]

pipeline = MockPipeline(instructions)
if_stage = pipeline.stages['IF']
id_stage = pipeline.stages['ID']

# Cycle 1
print("ciclu1")
if_stage.execute()
print(f"IF: {if_stage.instruction}")
print(f"ID: {id_stage.instruction}")

print("\n ciclu2")
id_stage.execute()
if_stage.execute()
print(f"IF: {if_stage.instruction}")
print(f"ID: {id_stage.instruction}")
if id_stage.instruction:
    print(f"ID data: {id_stage.data}")

print("\n ciclu3")
id_stage.execute()
if_stage.execute()
print(f"IF: {if_stage.instruction}")
print(f"ID: {id_stage.instruction}")
if id_stage.instruction:
    print(f"ID data: {id_stage.data}")