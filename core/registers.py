
class RegisterFile:
    def __init__(self):
        self.registers = [0] * 32

    def read(self, reg):
        return 0 if reg == 0 else self.registers[reg]

    def write(self, reg, value):
    # aici am testat si branchless (self.regs[reg_num]= value*(reg_num!=0) )
    # insa este cu 8-10% mai lent
    # plus ca mi ar fi scris si in x0
        if reg != 0:

            self.registers[reg] = value

    def __str__(self):
        non_zero = {i: v for i, v in enumerate(self.registers) if v != 0}
        return f"Registrele: {non_zero}" if non_zero else "Toate registrele sunt 0"
if __name__ == "__main__":

    try:
        registers = RegisterFile()
        registers.write(13, 42)
        print(registers)
    except ValueError as ex:
        print(ex)

