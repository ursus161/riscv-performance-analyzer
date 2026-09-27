class Instruction:
    def __init__(self, opcode, rd=None, rs1=None, rs2=None, imm=None):
        self.opcode = opcode
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.pc = None
        self.source_line = None  # 0-indexed editor line, set by parser
        self._validate()

    def __str__(self):
        match self.opcode:
            case "add" | "sub" | "and" | "or" | "xor" | "sll" | "srl" | "sra" | "slt" | "sltu":
                return f"{self.opcode} x{self.rd}, x{self.rs1}, x{self.rs2}"
            case "addi" | "andi" | "ori" | "xori" | "slti" | "sltiu" | "slli" | "srli" | "srai":
                return f"{self.opcode} x{self.rd}, x{self.rs1}, {self.imm}"
            case "lw" | "lb" | "lh" | "lbu" | "lhu" | "jalr":
                return f"{self.opcode} x{self.rd}, {self.imm}(x{self.rs1})"
            case "sw" | "sb" | "sh":
                return f"{self.opcode} x{self.rs2}, {self.imm}(x{self.rs1})"
            case "beq" | "bne" | "blt" | "bge" | "bltu" | "bgeu":
                return f"{self.opcode} x{self.rs1}, x{self.rs2}, {self.imm}"
            case "lui" | "auipc":
                return f"{self.opcode} x{self.rd}, {self.imm}"
            case "jal":
                return f"jal x{self.rd}, {self.imm}"
            case _:
                return f"unknown opcode: {self.opcode}"

    def is_load(self):
        return self.opcode in ["lw", "lb", "lh", "lbu", "lhu"]

    def is_store(self):
        return self.opcode in ["sw", "sb", "sh"]

    def is_branch(self):
        return self.opcode in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]

    def is_jump(self):
        return self.opcode in ["jal", "jalr"]

    def is_alu(self):
        return self.opcode in [
            "add", "addi", "sub",
            "and", "andi", "or", "ori", "xor", "xori",
            "sll", "slli", "srl", "srli", "sra", "srai",
            "slt", "sltu", "slti", "sltiu",
            "lui", "auipc",
        ]

    def _validate(self):
        match self.opcode:
            case "add" | "sub" | "and" | "or" | "xor" | "sll" | "srl" | "sra" | "slt" | "sltu":
                if self.rd is None or self.rs1 is None or self.rs2 is None:
                    raise ValueError(f"{self.opcode} necesita rd, rs1, rs2")

            case "addi" | "andi" | "ori" | "xori" | "slti" | "sltiu" | "slli" | "srli" | "srai":
                if self.rd is None or self.rs1 is None or self.imm is None:
                    raise ValueError(f"{self.opcode} necesita rd, rs1, imm")

            case "lw" | "lb" | "lh" | "lbu" | "lhu" | "jalr":
                if self.rd is None or self.rs1 is None or self.imm is None:
                    raise ValueError(f"{self.opcode} necesita rd, rs1, imm")

            case "sw" | "sb" | "sh":
                if self.rs1 is None or self.rs2 is None or self.imm is None:
                    raise ValueError(f"{self.opcode} necesita rs1, rs2, imm")

            case "beq" | "bne" | "blt" | "bge" | "bltu" | "bgeu":
                if self.rs1 is None or self.rs2 is None or self.imm is None:
                    raise ValueError(f"{self.opcode} necesita rs1, rs2, imm")

            case "lui" | "auipc":
                if self.rd is None or self.imm is None:
                    raise ValueError(f"{self.opcode} necesita rd, imm")

            case "jal":
                if self.rd is None or self.imm is None:
                    raise ValueError(f"jal necesita rd, imm")

            case _:
                raise ValueError(f"opcode invalid: {self.opcode}")
