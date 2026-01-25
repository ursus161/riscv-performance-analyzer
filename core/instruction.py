class Instruction:
    def __init__(self, opcode, rd=None, rs1=None, rs2=None, imm=None):
        self.opcode = opcode
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.pc = None
        self._validate()

    def __str__(self):
        match self.opcode:
            case "add" | "sub" | "and" | "or" | "xor":
                return f"{self.opcode} x{self.rd}, x{self.rs1}, x{self.rs2}"
            case "addi":
                return f"addi x{self.rd}, x{self.rs1}, {self.imm}"
            case "lw":
                return f"lw x{self.rd}, {self.imm}(x{self.rs1})"
            case "sw":
                return f"sw x{self.rs2}, {self.imm}(x{self.rs1})"
            case "beq" | "bne":
                return f"{self.opcode} x{self.rs1}, x{self.rs2}, {self.imm}"
            case _:
                return f"unknown opcode: {self.opcode}"

    def is_load(self):
        return self.opcode == "lw"

    def is_store(self):
        return self.opcode == "sw"

    def is_branch(self):
        return self.opcode in ["beq", "bne"]

    def is_alu(self):
        return self.opcode in ["add", "addi", "sub", "and", "or", "xor"]

    def _validate(self):
        match self.opcode:
            case "add" | "sub" | "and" | "or" | "xor":
                if self.rd is None or self.rs1 is None or self.rs2 is None:
                    raise ValueError(f"{self.opcode} necesita rd, rs1, rs2")

            case "addi" | "lw":
                if self.rd is None or self.rs1 is None or self.imm is None:
                    raise ValueError(f"{self.opcode} necesita rd, rs1, imm")

            case "sw":
                if self.rs1 is None or self.rs2 is None or self.imm is None:
                    raise ValueError(f"sw necesita rs1, rs2, imm")

            case "beq" | "bne":
                if self.rs1 is None or self.rs2 is None or self.imm is None:
                    raise ValueError(f"{self.opcode} necesita rs1, rs2, imm")

            case _:
                raise ValueError(f"opcode invalid: {self.opcode}")