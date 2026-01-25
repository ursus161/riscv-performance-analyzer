class PipelineStage:
    def __init__(self, name):
        self.name = name
        self.instruction = None
        self.data = {}

class IFStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("IF")
        self.pipeline = pipeline

    def execute(self):
        if self.pipeline.pc >= len(self.pipeline.instructions):
            self.instruction = None
            return

        self.instruction = self.pipeline.instructions[self.pipeline.pc]
        self.instruction.pc = self.pipeline.pc
        self.pipeline.pc += 1


class IDStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("ID")
        self.pipeline = pipeline

    def execute(self):
        self.instruction = self.pipeline.stages['IF'].instruction
        self.pipeline.stages['IF'].instruction = None

        if self.instruction is None:
            return

        if self.instruction.rs1 is not None:
            self.data['rs1_value'] = self.pipeline.registers.read(self.instruction.rs1)

        if self.instruction.rs2 is not None:
            self.data['rs2_value'] = self.pipeline.registers.read(self.instruction.rs2)


class EXStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("EX")
        self.pipeline = pipeline

    def execute(self):
        self.instruction = self.pipeline.stages['ID'].instruction
        prev_data = self.pipeline.stages['ID'].data
        self.pipeline.stages['ID'].instruction = None

        if self.instruction is None:
            return

        match self.instruction.opcode:
            case "add":
                self.data['result'] = prev_data['rs1_value'] + prev_data['rs2_value']

            case "sub":
                self.data['result'] = prev_data['rs1_value'] - prev_data['rs2_value']

            case "and":
                self.data['result'] = prev_data['rs1_value'] & prev_data['rs2_value']

            case "or":
                self.data['result'] = prev_data['rs1_value'] | prev_data['rs2_value']

            case "xor":
                self.data['result'] = prev_data['rs1_value'] ^ prev_data['rs2_value']

            case "addi":
                self.data['result'] = prev_data['rs1_value'] + self.instruction.imm

            case "lw":
                self.data['address'] = prev_data['rs1_value'] + self.instruction.imm

            case "sw":
                self.data['address'] = prev_data['rs1_value'] + self.instruction.imm
                self.data['store_value'] = prev_data['rs2_value']

            case "beq" | "bne":
                taken = (prev_data['rs1_value'] == prev_data['rs2_value']) if self.instruction.opcode == "beq" else (
                            prev_data['rs1_value'] != prev_data['rs2_value'])
                self.data['branch_taken'] = taken
                if taken:
                    self.data['branch_target'] = self.instruction.pc + self.instruction.imm


class MEMStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("MEM")
        self.pipeline = pipeline

    def execute(self):
        self.instruction = self.pipeline.stages['EX'].instruction
        prev_data = self.pipeline.stages['EX'].data
        self.pipeline.stages['EX'].instruction = None

        if self.instruction is None:
            return

        if self.instruction.is_load():
            address = prev_data['address']
            self.data['result'] = self.pipeline.memory.read(address)

        elif self.instruction.is_store():
            address = prev_data['address']
            value = prev_data['store_value']
            self.pipeline.memory.write(address, value)

        else:
            self.data['result'] = prev_data.get('result')


class WBStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("WB")
        self.pipeline = pipeline

    def execute(self):
        self.instruction = self.pipeline.stages['MEM'].instruction
        prev_data = self.pipeline.stages['MEM'].data
        self.pipeline.stages['MEM'].instruction = None

        if self.instruction is None:
            return

        if not self.instruction.is_store() and self.instruction.rd is not None:
            result = prev_data.get('result', 0)
            self.pipeline.registers.write(self.instruction.rd, result)