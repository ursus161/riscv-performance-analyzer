from math import inf

from core.registers import RegisterFile
from core.memory import Memory
from core.branch_predictor import PerceptronPredictor, BTB
from pipeline.stages import IFStage, IDStage, EXStage, MEMStage, WBStage


class Pipeline:
    def __init__(self, instructions, cache=None, verbose=False, use_branch_predictor=False):
        self.instructions = instructions
        self.registers = RegisterFile()
        self.memory = Memory(cache=cache)
        self.pc = 0
        self.cycle = 0
        self.executed_count = 0
        self.verbose = verbose
        self.branch_predictor = PerceptronPredictor() if use_branch_predictor else None
        self.btb = BTB() if use_branch_predictor else None

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

        ex_instr = self.stages['EX'].instruction
        if ex_instr and (ex_instr.is_branch() or ex_instr.is_jump()):
            actual_taken = self.stages['EX'].data.get('branch_taken', False)
            actual_target = self.stages['EX'].data.get('branch_target')

            if actual_taken and self.btb:
                self.btb.update(ex_instr.pc, actual_target)

            if ex_instr.is_branch() and self.branch_predictor:
                predicted_taken = getattr(ex_instr, 'predicted_taken', False)
                predicted_target = getattr(ex_instr, 'predicted_target', None)
                self.branch_predictor.update(ex_instr.pc, actual_taken)

                direction_wrong = predicted_taken != actual_taken
                target_wrong = actual_taken and predicted_target != actual_target

                if direction_wrong or target_wrong:
                    self.pc = actual_target if actual_taken else ex_instr.pc + 1
                    self.stages['IF'].instruction = None
                    self.stages['ID'].instruction = None

            elif ex_instr.is_jump():
                predicted_target = getattr(ex_instr, 'predicted_target', None)
                if predicted_target != actual_target:
                    self.pc = actual_target
                    self.stages['IF'].instruction = None
                    self.stages['ID'].instruction = None

            else:
                if actual_taken:
                    self.pc = actual_target
                    self.stages['IF'].instruction = None
                    self.stages['ID'].instruction = None

        self.cycle += 1
    #to be modified if you want to prevent infinite loops
    #set to 'inf' for testing
    def run(self, max_cycles= inf):
        while self.cycle < max_cycles:
            self.tick()

            if not self.is_done() and self.verbose:
                print(self)
            elif not self.is_done():
                continue
            else:
                break
        if self.verbose:
            print(f"\nfinal state")
            print(f"cicluri ceas: {self.cycle}")
            print(f"registri: {self.registers}")
            print(f"memoria principala: {self.memory}")

            if self.memory.cache:
                print(f"\ncache performance:")
                self.memory.cache.print_stats()

    def is_done(self):
        return all(stage.instruction is None for stage in self.stages.values())


    def get_performance_stats(self):
        total_instructions = self.executed_count
        cpi = self.cycle / total_instructions if total_instructions > 0 else 0

        stats = {
            'total_cycles': self.cycle,
            'total_instructions': total_instructions,
            'cpi': cpi,
            'ipc': 1 / cpi if cpi > 0 else 0,
        }

        if self.branch_predictor:
            stats['branch_predictor'] = self.branch_predictor.get_stats()

        if self.btb:
            stats['btb'] = self.btb.get_stats()

        return stats

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

    def mem_is_stalled(self):
        return self.stages['MEM'].stall_cycles > 0