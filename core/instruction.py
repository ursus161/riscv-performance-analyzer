#aici vreau sa imi definesc clasa instructiunii cu toate metodele definiitorii de riguoare


class Instruction:

    def __init__(self, opcode, rd=None, rs1=None, rs2=None, imm=None):
        #le initializez cu None pt ca pot sa am (sw x12, 0(gp)), care nu are niciun rs2
        self.opcode = opcode
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self._validate()


    def __str__(self):
        match self.opcode:
            case "add":
                return f"add x{self.rd}, x{self.rs1}, x{self.rs2}"
            case "sub":
                return f"sub x{self.rd}, x{self.rs1}, x{self.rs2}"
            case "and":
                return f"and x{self.rd}, x{self.rs1}, x{self.rs2}"
            case "or":
                return f"or x{self.rd}, x{self.rs1}, x{self.rs2}"
            case "xor":
                return f"xor x{self.rd}, x{self.rs1}, x{self.rs2}"
            case "addi":
                return f"addi x{self.rd}, x{self.rs1}, {self.imm}"
            case "lw":
                return f"lw x{self.rd}, {self.imm}(x{self.rs1})"
            case "sw":
                return f"sw x{self.rs2}, {self.imm}(x{self.rs1})"
            case "beq":
                return f"beq x{self.rs1}, x{self.rs2}, {self.imm}"
            case "bne":
                return f"bne x{self.rs1}, x{self.rs2}, {self.imm}"
            case _:
                return f"{self.opcode} nu exista acest opcode"

    def isloadword(self):
        return self.opcode == "lw"

    def isstoreword(self):
        return self.opcode == "sw"

    def ismemorydependent(self):
        return self.opcode == "sw" or self.opcode == "lw"

    def isbranch(self):
        return self.opcode in ["bne", "beq"]

    def isalu(self):
        return self.opcode in ["add", "addi", "sub", "and", "or", "xor"]

    def _validate(self):
        match self.opcode:
            # r-type
            case "add" | "sub" | "and" | "or" | "xor":
                if self.rd is None or self.rs1 is None or self.rs2 is None:
                    raise ValueError(f"{self.opcode} necesita rd, rs1, rs2")

            # i-type
            case "addi" | "lw":
                if self.rd is None or self.rs1 is None or self.imm is None:
                    raise ValueError(f"{self.opcode} necesita rd, rs1, imm")

            # s-type
            case "sw":
                if self.rs1 is None or self.rs2 is None or self.imm is None:
                    raise ValueError(f"sw necesita rs1, rs2, imm")

            # b-type
            case "beq" | "bne":
                if self.rs1 is None or self.rs2 is None or self.imm is None:
                    raise ValueError(f"{self.opcode} necesita rs1, rs2, imm")

            # greseli, teste, typo uri etc
            case _:
                raise ValueError(f"nu exista: {self.opcode}")


if __name__ == "__main__":
    lw = Instruction("lw",15,15,None, 20 )
    try:
        print(lw.isloadword())
        print(lw.isstoreword())
    except ValueError as e:
        print(e)

