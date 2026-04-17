from core.instruction import Instruction

DATA_BASE = 0x400  # baza sectiunii .data (1024, incape in 12-bit signed imm) e practic doar o adresa ram baselien


class AssemblyParser:
    def __init__(self, filename):
        self.filename = filename
        self.instructions = []
        self.labels = {}       # code labels -> pc index
        self.data_labels = {}  # data labels -> byte address
        self.initial_memory = {}
        self._data_ptr = DATA_BASE
        self._section = 'text'
        self.abi_names = {
            'zero': 0,
            'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7,
            's0': 8, 'fp': 8,
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

        self._first_pass(lines)
        self._second_pass(lines)

        return self.instructions, self.initial_memory

    def _clean(self, line):
        return line.split('#')[0].strip()

    def _is_directive(self, line):
        return line.startswith('.')

    def _first_pass(self, lines):
        pc = 0
        for line in lines:
            line = self._clean(line)
            if not line:
                continue

            if self._is_directive(line):
                self._handle_directive_first_pass(line)
                continue

            if self._section == 'data':
                if ':' in line:
                    label = line.split(':')[0].strip()
                    self.data_labels[label] = self._data_ptr
                continue

            if ':' in line:
                label, _, rest = line.partition(':')
                self.labels[label.strip()] = pc
                if rest.strip():
                    pc += 1
            else:
                pc += 1

    def _handle_directive_first_pass(self, line):
        parts = line.replace(',', '').split()
        directive = parts[0].lower()

        match directive:
            case '.data':
                self._section = 'data'
            case '.text':
                self._section = 'text'
            case '.word':
                for v in parts[1:]:
                    self.initial_memory[self._data_ptr] = int(v, 0)
                    self._data_ptr += 4
            case '.space':
                self._data_ptr += int(parts[1], 0)
            case _:
                pass  # .globl, .global, .align etc -> skip

    def _second_pass(self, lines):
        section = 'text'
        for line in lines:
            line = self._clean(line)
            if not line:
                continue

            if self._is_directive(line):
                d = line.split()[0].lower()
                if d == '.data':
                    section = 'data'
                elif d == '.text':
                    section = 'text'
                continue

            if section == 'data':
                continue

            if ':' in line:
                _, _, rest = line.partition(':')
                line = rest.strip()
                if not line:
                    continue

            instr = self._parse_instruction(line)
            if instr:
                self.instructions.append(instr)

    def _resolve_imm(self, token):
        if token in self.data_labels:
            return self.data_labels[token]
        return int(token, 0)

    def _parse_instruction(self, line):
        parts = line.replace(',', '').split()
        opcode = parts[0].lower()

        match opcode:
            case 'add' | 'sub' | 'and' | 'or' | 'xor' | 'sll' | 'srl' | 'sra':
                return self._parse_r_type(opcode, parts[1:])

            case 'addi' | 'andi' | 'ori' | 'xori' | 'slti' | 'sltiu':
                return self._parse_i_type(opcode, parts[1:])

            case 'slli' | 'srli' | 'srai':
                return self._parse_i_type(opcode, parts[1:])

            case 'lw':
                return self._parse_load(opcode, parts[1:])

            case 'sw':
                return self._parse_store(opcode, parts[1:])

            case 'beq' | 'bne' | 'blt' | 'bge' | 'bltu' | 'bgeu':
                return self._parse_branch(opcode, parts[1:])

            case 'lui' | 'auipc':
                return self._parse_u_type(opcode, parts[1:])

            case 'jal':
                return self._parse_jal(parts[1:])

            case 'jalr':
                return self._parse_jalr(parts[1:])

            case 'la':
                return self._parse_la(parts[1:])

            case _:
                print(f"Warning: Unknown instruction '{opcode}'")
                return None

    def _parse_r_type(self, opcode, args):
        rd  = self._parse_register(args[0])
        rs1 = self._parse_register(args[1])
        rs2 = self._parse_register(args[2])
        return Instruction(opcode, rd=rd, rs1=rs1, rs2=rs2)

    def _parse_i_type(self, opcode, args):
        rd  = self._parse_register(args[0])
        rs1 = self._parse_register(args[1])
        imm = self._resolve_imm(args[2])
        return Instruction(opcode, rd=rd, rs1=rs1, imm=imm)

    def _parse_load(self, opcode, args):
        rd = self._parse_register(args[0])
        offset_base = args[1]

        if '(' in offset_base:
            offset, base = offset_base.split('(')
            rs1 = self._parse_register(base.rstrip(')'))
            imm = int(offset, 0) if offset else 0
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
            imm = int(offset, 0) if offset else 0
        else:
            rs1 = self._parse_register(offset_base)
            imm = 0

        return Instruction(opcode, rs1=rs1, rs2=rs2, imm=imm)

    def _parse_branch(self, opcode, args):
        rs1 = self._parse_register(args[0])
        rs2 = self._parse_register(args[1])
        target = args[2]

        if target in self.labels:
            imm = self.labels[target] - len(self.instructions)
        else:
            imm = int(target, 0)

        return Instruction(opcode, rs1=rs1, rs2=rs2, imm=imm)

    def _parse_u_type(self, opcode, args):
        rd  = self._parse_register(args[0])
        imm = self._resolve_imm(args[1])
        return Instruction(opcode, rd=rd, imm=imm)

    def _parse_jal(self, args):
        rd = self._parse_register(args[0])
        target = args[1]

        if target in self.labels:
            imm = self.labels[target] - len(self.instructions)
        else:
            imm = int(target, 0)

        return Instruction('jal', rd=rd, imm=imm)

    def _parse_jalr(self, args):
        rd = self._parse_register(args[0])

        if len(args) == 2 and '(' in args[1]:
            offset, base = args[1].split('(')
            rs1 = self._parse_register(base.rstrip(')'))
            imm = int(offset, 0) if offset else 0
        else:
            rs1 = self._parse_register(args[1])
            imm = int(args[2], 0) if len(args) > 2 else 0

        return Instruction('jalr', rd=rd, rs1=rs1, imm=imm)

    def _parse_la(self, args):
        # pseudo: la rd, label -> addi rd, zero, addr
        rd    = self._parse_register(args[0])
        label = args[1]

        if label not in self.data_labels:
            raise ValueError(f"Unknown data label: '{label}'")

        return Instruction('addi', rd=rd, rs1=0, imm=self.data_labels[label])

    def _parse_register(self, reg_str):
        reg_str = reg_str.lower().strip()

        if reg_str in self.abi_names:
            return self.abi_names[reg_str]

        if reg_str.startswith('x'):
            try:
                num = int(reg_str[1:])
                if 0 <= num <= 31:
                    return num
            except ValueError:
                pass

        raise ValueError(f"Invalid register: '{reg_str}'")


def parse_assembly(filename):
    parser = AssemblyParser(filename)
    return parser.parse()
