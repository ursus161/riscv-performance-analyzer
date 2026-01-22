
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

if __name__ == "__main__":
  pass
