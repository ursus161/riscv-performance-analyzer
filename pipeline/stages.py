
class PipelineStage:
    def __init__(self,name):
        self.name = name #if,id,ex,mem,wb
        self.instruction = None #insturctiunea la care lucreaza stage ul name
        self.data = {} #rez, adrese, etc

    def execute(self):
        raise NotImplementedError(f"nu e implementata inca instructiunea {self.name}")


class IFStage(PipelineStage):

    def __init__(self, pipeline):
        super().__init__("IF")
        self.pipeline = pipeline

    def execute(self):

        # daca mai sunt instructiuni
        if self.pipeline.pc >= len(self.pipeline.instructions):
            self.instruction = None
            return

        # fetch
        self.instruction = self.pipeline.instructions[self.pipeline.pc]


        self.pipeline.pc += 1


class IDStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("ID")
        self.pipeline = pipeline

    def execute(self):
        #ia din IF ul anterior ei
        self.instruction = self.pipeline.stages['IF'].instruction

        # curata IF (instructiunea a avansat)
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
            case "add" | "sub" | "and" | "or" | "xor":
                rs1_val = prev_data['rs1_value']
                rs2_val = prev_data['rs2_value']

                match self.instruction.opcode:
                    case "add":
                        self.data['result'] = rs1_val + rs2_val
                    case "sub":
                        self.data['result'] = rs1_val - rs2_val
                    case "and":
                        self.data['result'] = rs1_val & rs2_val
                    case "or":
                        self.data['result'] = rs1_val | rs2_val
                    case "xor":
                        self.data['result'] = rs1_val ^ rs2_val

            case "addi":
                self.data['result'] = prev_data['rs1_value'] + self.instruction.imm

            case "lw":
                self.data['address'] = prev_data['rs1_value'] + self.instruction.imm

            case "sw":
                self.data['address'] = prev_data['rs1_value'] + self.instruction.imm
                self.data['store_value'] = prev_data['rs2_value']
                #din store_value se va scrie in adresa la MEM stage

            case "beq" | "bne":
                rs1_val = prev_data['rs1_value']
                rs2_val = prev_data['rs2_value']

                taken = (rs1_val == rs2_val) if self.instruction.opcode == "beq" else (rs1_val != rs2_val)
                self.data['branch_taken'] = taken

                if taken:
                    self.data['branch_target'] = self.pipeline.pc + self.instruction.imm





if __name__ == "__main__":
  pass
