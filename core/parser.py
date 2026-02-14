from core.instruction import Instruction


class AssemblyParser:
    def __init__(self, filename):
        self.filename = filename
        self.instructions = []
        self.labels = {}
        #maparea x(num) la ABI convention
        self.abi_names = {
            'zero': 0,
            'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7,
            's0': 8, 'fp': 8, # s0 si fp sunt la fel, insa in simulatoare precum ripes.me putem folosi doar s0
            's1': 9,
            'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13,
            'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
            's2': 18, 's3': 19, 's4': 20, 's5': 21,
            's6': 22, 's7': 23, 's8': 24, 's9': 25,
            's10': 26, 's11': 27,
            't3': 28, 't4': 29, 't5': 30, 't6': 31
        }

    def parse(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self._first_pass(lines) #doua treceri in caz ca am branch uri si trebuie sa imi recunoasca label ul la taken
        self._second_pass(lines)

        return self.instructions

    def _first_pass(self, lines):
        pc = 0
        #first pass a fost gandit ptr labels (loop etc), iar 2nd pass pentru insturctiuni
        #o sa am cv in genul self.labels = {'loop':67, 'end': 90}
        for line in lines:
            line = line.split('#')[0].strip() # ca sa sterg comentariile

            if not line:
                continue

            if ':' in line:
                label = line.split(':')[0].strip() #label gasit
                self.labels[label] = pc
            else:
                pc += 1

    def _second_pass(self, lines):
        for line in lines:
            line = line.split('#')[0].strip()

            if not line or ':' in line:
                continue

            instr = self._parse_instruction(line)
            if instr:
                self.instructions.append(instr)

    def _parse_instruction(self, line):
        parts = line.replace(',', '').split()
        opcode = parts[0].lower()

        match opcode:
            case 'add' | 'sub' | 'and' | 'or' | 'xor':
                return self._parse_r_type(opcode, parts[1:])

            case 'addi':
                return self._parse_i_type(opcode, parts[1:])

            case 'lw':
                return self._parse_load(opcode, parts[1:])

            case 'sw':
                return self._parse_store(opcode, parts[1:])

            case 'bne' | 'beq':
                return self._parse_branch(opcode, parts[1:])

            case _:
                print(f"Warning: Unknown instruction '{opcode}'")
                return None

    def _parse_r_type(self, opcode, args):
        rd = self._parse_register(args[0])
        rs1 = self._parse_register(args[1])
        rs2 = self._parse_register(args[2])
        return Instruction(opcode, rd=rd, rs1=rs1, rs2=rs2)

    def _parse_i_type(self, opcode, args):
        rd = self._parse_register(args[0])
        rs1 = self._parse_register(args[1])
        imm = int(args[2])
        return Instruction(opcode, rd=rd, rs1=rs1, imm=imm)

    def _parse_load(self, opcode, args):
        rd = self._parse_register(args[0])
        offset_base = args[1]

        if '(' in offset_base:
            offset, base = offset_base.split('(')
            rs1 = self._parse_register(base.rstrip(')'))
            imm = int(offset) if offset else 0
        else:
            rs1 = self._parse_register(offset_base)
            imm = 0

        return Instruction(opcode, rd=rd, rs1=rs1, imm=imm)

    def _parse_store(self, opcode, args):
        rs2 = self._parse_register(args[0])
        offset_base = args[1]

        if '(' in offset_base:
            offset, base = offset_base.split('(')
            rs1 = self._parse_register(base.rstrip(')'))
            imm = int(offset) if offset else 0
        else:
            rs1 = self._parse_register(offset_base)
            imm = 0

        return Instruction(opcode, rs1=rs1, rs2=rs2, imm=imm)

    def _parse_branch(self, opcode, args):
        rs1 = self._parse_register(args[0])
        rs2 = self._parse_register(args[1])

        target = args[2]
        if target in self.labels:
            target_pc = self.labels[target]
            current_pc = len(self.instructions)
            imm = target_pc - current_pc
        else:
            imm = int(target)

        return Instruction(opcode, rs1=rs1, rs2=rs2, imm=imm)

    def _parse_register(self, reg_str):
        reg_str = reg_str.lower().strip()


       # abi il am deja in memorie, e mai cost eff sa l verific primul
        if reg_str in self.abi_names:
            return self.abi_names[reg_str]

        if reg_str.startswith('x'):
            try:
                num = int(reg_str[1:])
                if 0 <= num <= 31:
                    return num
            except ValueError:
                pass


        raise ValueError(f"Invalid register: {reg_str}")


def parse_assembly(filename):
    parser = AssemblyParser(filename)
    return parser.parse()