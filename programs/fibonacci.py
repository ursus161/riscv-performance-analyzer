from core.instruction import Instruction


def get_program():
    return [
        Instruction("addi", rd=1, rs1=0, imm=5),
        Instruction("addi", rd=2, rs1=0, imm=0),
        Instruction("addi", rd=3, rs1=0, imm=1),

        Instruction("add", rd=4, rs1=2, rs2=3),
        Instruction("add", rd=2, rs1=3, rs2=0),
        Instruction("add", rd=3, rs1=4, rs2=0),
        Instruction("addi", rd=1, rs1=1, imm=-1),
        Instruction("add", rd=0, rs1=0, rs2=0),       # PC=7-9: NOP pt hazard de date fix temporar
        Instruction("add", rd=0, rs1=0, rs2=0),
        Instruction("add", rd=0, rs1=0, rs2=0),
        Instruction("bne", rs1=1, rs2=0, imm=-7),
    ]