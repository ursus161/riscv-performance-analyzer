class PipelineStage:
    def __init__(self, name):
        self.name = name
        self.instruction = None
        self.data = {}

    def clear_data(self):
        self.data = {}

class IFStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("IF")
        self.pipeline = pipeline

    def execute(self):
        self.clear_data()
        if self.pipeline.mem_is_stalled():
            return
        if self.instruction is not None:
            return #daca am deja un stall, nu mai iau alta

        if self.pipeline.pc >= len(self.pipeline.instructions):
            self.instruction = None
            return

        instr = self.pipeline.instructions[self.pipeline.pc]
        instr.pc = self.pipeline.pc
        self.pipeline.pc += 1
        self.instruction = instr

        if instr.is_branch() and self.pipeline.branch_predictor:
            predicted, _ = self.pipeline.branch_predictor.predict(instr.pc)
            instr.predicted_taken = predicted
            if predicted:
                target = self.pipeline.btb.lookup(instr.pc) if self.pipeline.btb else None
                instr.predicted_target = target
                if target is not None:
                    self.pipeline.pc = target

        elif instr.is_jump() and self.pipeline.btb:
            target = self.pipeline.btb.lookup(instr.pc)
            instr.predicted_target = target
            if target is not None:
                self.pipeline.pc = target


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
        if self.pipeline.mem_is_stalled():
            return

        self.instruction = self.pipeline.stages['IF'].instruction

        self.clear_data()
        if self.instruction is None:
            return

        if self._detect_load_use_hazard():
            # stall
            self.pipeline.stages['IF'].instruction = self.instruction #aici dau feed la stall
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

    def _get_forwarded_value(self, reg):
        if reg == 0:
            return None  # x0 e hardwired zero, nu forwardez niciodata

        ex_instr = self.pipeline.stages['EX'].instruction
        if ex_instr and ex_instr.rd == reg and not ex_instr.is_store():
            ex_data = self.pipeline.stages['EX'].data
            if 'result' in ex_data:
                return ex_data['result']

        mem_instr = self.pipeline.stages['MEM'].instruction
        if mem_instr and mem_instr.rd == reg and not mem_instr.is_store():
            mem_data = self.pipeline.stages['MEM'].data
            if 'result' in mem_data:
                return mem_data['result']

        # WB ruleaza înaintea ID în fiecare ciclu, deci registrele sunt deja actualizate
        return None


class EXStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("EX")
        self.pipeline = pipeline

    def execute(self):
        if self.pipeline.mem_is_stalled():
            return

        self.instruction = self.pipeline.stages['ID'].instruction
        prev_data = self.pipeline.stages['ID'].data
        self.pipeline.stages['ID'].instruction = None

        self.clear_data()


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

            case "lw" | "lb" | "lh" | "lbu" | "lhu":
                self.data['address'] = prev_data['rs1_value'] + self.instruction.imm

            case "sw" | "sb" | "sh":
                self.data['address'] = prev_data['rs1_value'] + self.instruction.imm
                self.data['store_value'] = prev_data['rs2_value']

            case "slt":
                self.data['result'] = 1 if prev_data['rs1_value'] < prev_data['rs2_value'] else 0
            case "sltu":
                self.data['result'] = 1 if (prev_data['rs1_value'] & 0xFFFFFFFF) < (prev_data['rs2_value'] & 0xFFFFFFFF) else 0
            case "sll":
                self.data['result'] = prev_data['rs1_value'] << (prev_data['rs2_value'] & 0x1F)
            case "srl":
                self.data['result'] = (prev_data['rs1_value'] & 0xFFFFFFFF) >> (prev_data['rs2_value'] & 0x1F)
            case "sra":
                self.data['result'] = prev_data['rs1_value'] >> (prev_data['rs2_value'] & 0x1F)

            case "andi":
                self.data['result'] = prev_data['rs1_value'] & self.instruction.imm
            case "ori":
                self.data['result'] = prev_data['rs1_value'] | self.instruction.imm
            case "xori":
                self.data['result'] = prev_data['rs1_value'] ^ self.instruction.imm
            case "slti":
                self.data['result'] = 1 if prev_data['rs1_value'] < self.instruction.imm else 0
            case "sltiu":
                self.data['result'] = 1 if (prev_data['rs1_value'] & 0xFFFFFFFF) < (self.instruction.imm & 0xFFFFFFFF) else 0
            case "slli":
                self.data['result'] = prev_data['rs1_value'] << (self.instruction.imm & 0x1F)
            case "srli":
                self.data['result'] = (prev_data['rs1_value'] & 0xFFFFFFFF) >> (self.instruction.imm & 0x1F)
            case "srai":
                self.data['result'] = prev_data['rs1_value'] >> (self.instruction.imm & 0x1F)

            case "lui":
                self.data['result'] = self.instruction.imm << 12
            case "auipc":
                self.data['result'] = self.instruction.pc + (self.instruction.imm << 12)

            case "beq" | "bne" | "blt" | "bge" | "bltu" | "bgeu":
                a, b = prev_data['rs1_value'], prev_data['rs2_value']
                match self.instruction.opcode:
                    case "beq":  taken = a == b
                    case "bne":  taken = a != b
                    case "blt":  taken = a < b
                    case "bge":  taken = a >= b
                    case "bltu": taken = (a & 0xFFFFFFFF) < (b & 0xFFFFFFFF)
                    case "bgeu": taken = (a & 0xFFFFFFFF) >= (b & 0xFFFFFFFF)
                self.data['branch_taken'] = taken
                if taken:
                    self.data['branch_target'] = self.instruction.pc + self.instruction.imm

            case "jal":
                self.data['result'] = self.instruction.pc + 1  # return address
                self.data['branch_taken'] = True
                self.data['branch_target'] = self.instruction.pc + self.instruction.imm

            case "jalr":
                self.data['result'] = self.instruction.pc + 1  # return address
                self.data['branch_taken'] = True
                self.data['branch_target'] = prev_data['rs1_value'] + self.instruction.imm


class MEMStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("MEM")
        self.pipeline = pipeline
        self.stall_cycles = 0

    def execute(self):
        if self.stall_cycles > 0:
            self.stall_cycles -= 1
            return

        self.instruction = self.pipeline.stages['EX'].instruction
        prev_data = self.pipeline.stages['EX'].data
        self.pipeline.stages['EX'].instruction = None

        self.clear_data()

        if self.instruction is None:
            return

        if self.instruction.is_load():
            address = prev_data['address']
            if self.pipeline.memory.cache:
                hit, latency = self.pipeline.memory.cache.access(address, is_write=False)
                self.pipeline.memory.total_latency += latency
                if not hit:
                    self.pipeline.memory.ram_accesses += 1
                self.stall_cycles = latency - 1
            else:
                self.pipeline.memory.ram_accesses += 1
                self.stall_cycles = self.pipeline.ram_latency - 1
            match self.instruction.opcode:
                case "lw":
                    self.data['result'] = self.pipeline.memory.read(address)
                case "lh":
                    raw = self.pipeline.memory.read(address, 2)
                    # xor flippeaza sign bit-ul, scazand 0x8000 translateaza in negativ daca era setat
                    # ex: 0xFF80 ^ 0x8000 = 0x7F80, 0x7F80 - 0x8000 = -128
                    # translatie din unsigned in signed
                    self.data['result'] = (raw ^ 0x8000) - 0x8000
                case "lhu":
                    self.data['result'] = self.pipeline.memory.read(address, 2)
                case "lb":
                    raw = self.pipeline.memory.read(address, 1)
                    # acelasi truc, dar pe 8 biti: 0xFF ^ 0x80 = 0x7F, 0x7F - 0x80 = -1
                    self.data['result'] = (raw ^ 0x80) - 0x80
                case "lbu":
                    self.data['result'] = self.pipeline.memory.read(address, 1)

        elif self.instruction.is_store():
            address = prev_data['address']
            value = prev_data['store_value']
            if self.pipeline.memory.cache:
                hit, latency = self.pipeline.memory.cache.access(address, is_write=True)
                self.pipeline.memory.total_latency += latency
                if not hit:
                    self.pipeline.memory.ram_accesses += 1
                self.stall_cycles = latency - 1
            else:
                self.pipeline.memory.ram_accesses += 1
                self.stall_cycles = self.pipeline.ram_latency - 1
            match self.instruction.opcode:
                case "sw":
                    self.pipeline.memory.write(address, value)
                case "sh":
                    self.pipeline.memory.write(address, value, 2)
                case "sb":
                    self.pipeline.memory.write(address, value, 1)

        else:
            self.data['result'] = prev_data.get('result')


class WBStage(PipelineStage):
    def __init__(self, pipeline):
        super().__init__("WB")
        self.pipeline = pipeline

    def execute(self):
        if self.pipeline.mem_is_stalled():
            self.instruction = None
            self.clear_data()
            return

        self.instruction = self.pipeline.stages['MEM'].instruction
        prev_data = self.pipeline.stages['MEM'].data
        self.pipeline.stages['MEM'].instruction = None
        
        self.clear_data()

        if self.instruction is None:
            return

        self.pipeline.executed_count += 1

        if not self.instruction.is_store() and self.instruction.rd is not None:
            result = prev_data.get('result', 0)
            self.data['result'] = result
            self.pipeline.registers.write(self.instruction.rd, result)