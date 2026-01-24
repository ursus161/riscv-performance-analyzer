
from core.instruction import Instruction

from core.registers import RegisterFile
from core.memory import Memory
from pipeline.stages import IFStage, IDStage, EXStage, WBStage, MEMStage


class MockPipeline:
    def __init__(self, instructions):
        self.instructions = instructions
        self.pc = 0
        self.registers = RegisterFile()
        self.memory = Memory()

        self.stages = {
            'IF': IFStage(self),
            'ID': IDStage(self),
            'EX': EXStage(self),
            'MEM': MEMStage(self),
            'WB': WBStage(self)
        }


instructions = [
    Instruction("addi", rd=1, rs1=0, imm=5),
    Instruction("add", rd=2, rs1=1, rs2=1),
    Instruction("sw", rs1=0, rs2=2, imm=0)
]

pipeline = MockPipeline(instructions)
if_stage = pipeline.stages['IF']
id_stage = pipeline.stages['ID']
ex_stage = pipeline.stages['EX']
mem_stage= pipeline.stages['MEM']
wb_stage = pipeline.stages['WB']

print("ciclu 1")
if_stage.execute()
print(f"IF: {if_stage.instruction}")
print(f"ID: {id_stage.instruction}")
print(f"EX: {ex_stage.instruction}")

print("\nciclu 2")
id_stage.execute()
if_stage.execute()
print(f"IF: {if_stage.instruction}")
print(f"ID: {id_stage.instruction}")
if id_stage.instruction:
    print(f"ID data: {id_stage.data}")
print(f"EX: {ex_stage.instruction}")

print("\nciclu 3")
ex_stage.execute()
id_stage.execute()
if_stage.execute()
print(f"IF: {if_stage.instruction}")
print(f"ID: {id_stage.instruction}")
if id_stage.instruction:
    print(f"ID data: {id_stage.data}")
print(f"EX: {ex_stage.instruction}")
if ex_stage.instruction:
    print(f"EX data: {ex_stage.data}")

print("\nciclu4")
mem_stage.execute()
ex_stage.execute()
id_stage.execute()
if_stage.execute()
print(f"IF: {if_stage.instruction}")
print(f"ID: {id_stage.instruction}")
if id_stage.instruction:
    print(f"id data: {id_stage.data}")
print(f"EX: {ex_stage.instruction}")
if ex_stage.instruction:
    print(f"EX data: {ex_stage.data}")

print("\nciclu5")
wb_stage.execute()
mem_stage.execute()
ex_stage.execute()
id_stage.execute()
if_stage.execute()
print(f"IF: {if_stage.instruction}")
print(f"ID: {id_stage.instruction}")
print(f"EX: {ex_stage.instruction}")
if ex_stage.instruction:
    print(f"EX data: {ex_stage.data}")

print("\nrezultat dupa rulare")
print(f"regs: {pipeline.registers}")