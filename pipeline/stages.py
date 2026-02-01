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

        if self.instruction is not None:
            return

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

    def _detect_load_use_hazard(self):

        ex_instr = self.pipeline.stages['EX'].instruction

        if ex_instr and ex_instr.is_load() and ex_instr.rd:
            if self.instruction.rs1 == ex_instr.rd or self.instruction.rs2 == ex_instr.rd:
                return True

        return False

    def execute(self):
        self.instruction = self.pipeline.stages['IF'].instruction


        if self.instruction is None:
            return

        if self._detect_load_use_hazard():
            # stall
            self.pipeline.stages['IF'].instruction = self.instruction
            self.instruction = None
            return

        self.pipeline.stages['IF'].instruction = None

        if self.instruction.rs1 is not None:
            self.data['rs1_value'] = self.pipeline.registers.read(self.instruction.rs1)

        if self.instruction.rs2 is not None:
            self.data['rs2_value'] = self.pipeline.registers.read(self.instruction.rs2)

        self._apply_forwarding()
        #id citeste registrele, deci aici implementez forwarding ul

    def _apply_forwarding(self):
        if self.instruction.rs1 is not None:
            forwarded_value = self._get_forwarded_value(self.instruction.rs1)

            if forwarded_value is not None:


                self.data['rs1_value'] = forwarded_value


        if self.instruction.rs2 is not None:

            forwarded_value = self._get_forwarded_value(self.instruction.rs2)
            if forwarded_value is not None:
                self.data['rs2_value'] = forwarded_value

    #ex->mem, incerc sa iau valoarea din ex daca e disponibila asap
    def _get_forwarded_value(self, reg):


        ex_instr = self.pipeline.stages['EX'].instruction
        if ex_instr and ex_instr.rd == reg and not ex_instr.is_store():
            #a doua conditie mi se pare vaga, vreau registrul rd sa fie cel de care am nevoie
            #adica efectiv aia e detectarea de hazard
            #si sa nu fie store pt ca store ul nu scrie in registru
            ex_data = self.pipeline.stages['EX'].data
            if 'result' in ex_data:
                return ex_data['result']


        mem_instr = self.pipeline.stages['MEM'].instruction
        if mem_instr and mem_instr.rd == reg and not mem_instr.is_store():
            mem_data = self.pipeline.stages['MEM'].data
            if 'result' in mem_data:

                return mem_data['result']

        #wb forwarding
        #problema intampinata in cazul load use hazard, la testarea pentru cache locality
        wb_instr = self.pipeline.stages['WB'].instruction
        if wb_instr and wb_instr.rd == reg and not wb_instr.is_store():
            wb_data = self.pipeline.stages['WB'].data
            if 'result' in wb_data:
                return wb_data['result']

        # daca nu vreau forward
        return None


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
            self.data['result'] = result
            self.pipeline.registers.write(self.instruction.rd, result)