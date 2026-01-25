from core.instruction import Instruction


def get_program():

    return [
        Instruction("addi", rd=1, rs1=0, imm=5), #addi x1, x0, 5
        Instruction("addi", rd=2, rs1=0, imm=3), #addi x2, x0, 3
        Instruction("add", rd=3, rs1=1, rs2=2), #add x3, x1, x2
    ]