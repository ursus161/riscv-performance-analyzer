class RegisterFile:
   #o clasa pt registri, la fel ca la instructiuni o sa fie definite metodele simple
    def __init__(self):
        self.regs = [0] * 32  # x0-x31 (evident am 32 registri in riscv), toate inițializate cu 0

    def read(self, reg_num):

        if reg_num == 0:
            return 0  # x0 este mereu 0
        return self.regs[reg_num]

    def write(self, reg_num, value):
        #aici am testat si branchless (self.regs[reg_num]= value*(reg_num!=0) insa este cu 8-10% mai lent
        #plus ca mi ar fi scris si in x0
        if reg_num:
            self.regs[reg_num] = value


    def __str__(self):

        non_zero = {i: v for i, v in enumerate(self.regs) if v != 0}
        if not non_zero:
            return "Toate registele sunt 0"
        return f"Registrele: {non_zero}"

if __name__ == "__main__":

    try:
        registers = RegisterFile()
        registers.write(13, 42)
        registers.read(13)
        print(registers)
    except ValueError as ex:
        print(ex)

