from core.registers import RegisterFile
from core.memory import Memory
from pipeline.stages import IFStage, IDStage, EXStage, MEMStage, WBStage


class Pipeline:
    def __init__(self, instructions, cache =None):
        self.instructions = instructions
        self.registers = RegisterFile()
        self.memory = Memory(cache=cache)
        self.pc = 0
        self.cycle = 0

        self.stages = {
            'IF': IFStage(self),
            'ID': IDStage(self),
            'EX': EXStage(self),
            'MEM': MEMStage(self),
            'WB': WBStage(self)
        }

    def tick(self):
        self.stages['WB'].execute()
        self.stages['MEM'].execute()
        self.stages['EX'].execute()
        self.stages['ID'].execute()
        self.stages['IF'].execute()

        if (ex_instr := self.stages['EX'].instruction) and ex_instr.is_branch():
            if self.stages['EX'].data.get('branch_taken', False):
                self.pc = self.stages['EX'].data['branch_target'] #daca s a luat branch ul, schimb pc ul

        self.cycle += 1

    def run(self, max_cycles=10 ** 3):
        while self.cycle < max_cycles:
            self.tick()

            if not self.is_done():
                print(self)
            else:
                break

        print(f"\nfinal state")
        print(f"cicluri ceas: {self.cycle-1}")
        print(f"registri: {self.registers}")
        print(f"memoria principala: {self.memory}")

        if self.memory.cache:
            print(f"\ncache performance:")
            self.memory.cache.print_stats()

    def is_done(self):
        return all(stage.instruction is None for stage in self.stages.values())

    def __str__(self):
        lines = [f"\n{'-' * 50}"]
        lines.append(f"ciclul {self.cycle}")
        lines.append(f"{'-' * 50}")

        for name in ['IF', 'ID', 'EX', 'MEM', 'WB']:
            stage = self.stages[name]
            instr_str = str(stage.instruction) if stage.instruction else "nimic"
            lines.append(f"{name:4}: {instr_str}")

            if stage.data:
                lines.append(f"      data: {stage.data}")

        return '\n'.join(lines)