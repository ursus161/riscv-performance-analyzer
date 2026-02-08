from core.instruction import Instruction
#exploatez cache ul ca sa testez codul scris de pana acum

def get_program():
    instructions = []

    base = 0x100
    valori = [10*i for i in range(1, 128 + 1)] # 10, 20, ..., 10*1024

    instructions.append(Instruction("addi", rd=11, rs1=0, imm=base))

    for i, val in enumerate(valori):

        instructions.append(Instruction("addi", rd=10, rs1=0, imm=val))
        instructions.append(Instruction("sw", rs1=11, rs2=10, imm=i * 4))


    instructions.append(Instruction("addi", rd=3, rs1=0, imm=0))


    for i in range(len(valori)):

        instructions.append(Instruction("lw", rd=10, rs1=11, imm=i * 4))


        instructions.append(Instruction("add", rd=3, rs1=3, rs2=10))

    return instructions
