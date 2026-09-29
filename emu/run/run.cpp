#include "run/run.hpp"

#include "decode/decoder.hpp"
#include "exec/execute.hpp"
#include "isa/reg.hpp"
#include "run/syscall.hpp"

namespace emu {

std::expected<void, Trap> step(Machine& m) {
    auto word = m.mem.load<std::uint32_t>(m.cpu.pc);
    if (!word) [[unlikely]] return std::unexpected(Trap{TrapCause::InstrAccessFault, m.cpu.pc});
    return execute(m, decode(*word));
}


RunResult run(Machine& m, std::uint64_t max_steps) {
    std::uint64_t steps = 0;
    while (max_steps == 0 || steps < max_steps) [[likely]] {
        auto result = step(m);
        ++steps; 
        if (result) [[likely]] continue;

        Trap trap = result.error();
        if (trap.cause != TrapCause::ECallM) return {StopReason::Trap, 0, trap, steps}; 
        //  a real fault (illegal instruction, bad memory access), stop the run.


        // UMODE(usermode): the emulator plays the kernel and serves the ecall.
        if (handle_syscall(m) == SyscallOutcome::Exit)
            return {StopReason::Exit, static_cast<std::int32_t>(m.cpu.reg(reg::a0)), trap, steps};

        m.cpu.pc += 4;  // the trap left pc on the ecall; resume after 
    }      
    return {StopReason::StepLimit, 0, Trap{}, steps};
}

} // namespace emu