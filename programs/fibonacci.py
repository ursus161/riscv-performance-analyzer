from core.instruction import Instruction


def get_program():
    return [
        # initializare
        Instruction("addi", rd=1, rs1=0, imm=4),  # PC=0: x1 = 4 (counter pt 4 iteratii)
        Instruction("addi", rd=2, rs1=0, imm=0),  # PC=1: x2 = 0 (fib(i-1))
        Instruction("addi", rd=3, rs1=0, imm=1),  # PC=2: x3 = 1 (fib(i))

        Instruction("add", rd=4, rs1=2, rs2=3),  # x4 = x2 + x3 (next fib)
        Instruction("add", rd=2, rs1=3, rs2=0),
        Instruction("add", rd=3, rs1=4, rs2=0),  
        Instruction("addi", rd=1, rs1=1, imm=-1),
        Instruction("bne", rs1=1, rs2=0, imm=-4),  # PC=7: if x1!=0 goto PC=3

        # done: x3 = 5
    ]